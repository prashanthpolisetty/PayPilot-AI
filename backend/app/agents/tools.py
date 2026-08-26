import json
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.db.models import Approval, Cart, Order, Payment
from app.services.catalog_service import CatalogService
from app.services.cart_service import CartService
from app.services.policy_engine import PolicyEngine
from app.services.razorpay_adapter import razorpay_adapter
from app.services.audit_service import AuditService

# Declarations of tool schemas for Gemini and Groq
TOOL_SCHEMAS = [
    {
        "name": "search_products",
        "description": "Search the merchant product catalog by keyword, category, price constraints, or features (e.g. ANC=True).",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Free text search term e.g. 'ANC Headphones'"},
                "category": {"type": "string", "description": "Product category e.g. 'Audio', 'Laptops', 'Accessories'"},
                "max_price": {"type": "number", "description": "Maximum price limit in Rupees (INR)"},
                "min_price": {"type": "number", "description": "Minimum price limit in Rupees (INR)"},
                "attributes": {"type": "object", "description": "Key-value pair filter e.g. {'ANC': true}"}
            }
        }
    },
    {
        "name": "get_product",
        "description": "Retrieve detailed authoritative product data by product_id or SKU.",
        "parameters": {
            "type": "object",
            "properties": {
                "product_id_or_sku": {"type": "string", "description": "The product ID or SKU code"}
            },
            "required": ["product_id_or_sku"]
        }
    },
    {
        "name": "check_inventory",
        "description": "Check whether a product has sufficient stock available.",
        "parameters": {
            "type": "object",
            "properties": {
                "product_id": {"type": "string"},
                "quantity": {"type": "integer"}
            },
            "required": ["product_id", "quantity"]
        }
    },
    {
        "name": "create_cart",
        "description": "Create a new empty shopping cart for a user and merchant.",
        "parameters": {
            "type": "object",
            "properties": {
                "user_id": {"type": "string"},
                "merchant_id": {"type": "string"}
            },
            "required": ["user_id", "merchant_id"]
        }
    },
    {
        "name": "add_to_cart",
        "description": "Add a product to the cart with specified quantity.",
        "parameters": {
            "type": "object",
            "properties": {
                "cart_id": {"type": "string"},
                "product_id": {"type": "string"},
                "quantity": {"type": "integer"}
            },
            "required": ["cart_id", "product_id"]
        }
    },
    {
        "name": "calculate_total",
        "description": "Recalculate and fetch the authoritative cart total from backend pricing.",
        "parameters": {
            "type": "object",
            "properties": {
                "cart_id": {"type": "string"}
            },
            "required": ["cart_id"]
        }
    },
    {
        "name": "check_policy",
        "description": "Run the deterministic Policy Engine on a cart to check for spending caps, quantity limits, and policy compliance.",
        "parameters": {
            "type": "object",
            "properties": {
                "cart_id": {"type": "string"},
                "user_id": {"type": "string"}
            },
            "required": ["cart_id", "user_id"]
        }
    },
    {
        "name": "request_user_approval",
        "description": "Request explicit human user approval for a money action.",
        "parameters": {
            "type": "object",
            "properties": {
                "cart_id": {"type": "string"},
                "user_id": {"type": "string"},
                "summary": {"type": "string", "description": "Pre-payment summary detailing item(s), price, and rationale"}
            },
            "required": ["cart_id", "user_id", "summary"]
        }
    },
    {
        "name": "create_payment_order",
        "description": "Create a Razorpay test-mode payment order after policy and user approval pass.",
        "parameters": {
            "type": "object",
            "properties": {
                "cart_id": {"type": "string"},
                "user_id": {"type": "string"}
            },
            "required": ["cart_id", "user_id"]
        }
    },
    {
        "name": "verify_payment",
        "description": "Verify Razorpay payment signature server-side and update order state to PAID.",
        "parameters": {
            "type": "object",
            "properties": {
                "order_id": {"type": "string"},
                "razorpay_payment_id": {"type": "string"},
                "razorpay_signature": {"type": "string"}
            },
            "required": ["order_id", "razorpay_payment_id", "razorpay_signature"]
        }
    },
    {
        "name": "simulate_payment_failure_recovery",
        "description": "Demonstrate graceful failure handling by executing a failed payment attempt and providing recovery recommendations.",
        "parameters": {
            "type": "object",
            "properties": {
                "order_id": {"type": "string"}
            },
            "required": ["order_id"]
        }
    }
]

class AgentToolExecutor:
    @staticmethod
    def execute_tool(db: Session, tool_name: str, tool_args: Dict[str, Any], user_id: str = "user_demo_001") -> Dict[str, Any]:
        try:
            if tool_name == "search_products":
                max_price_minor = int(tool_args["max_price"] * 100) if "max_price" in tool_args and tool_args["max_price"] else None
                min_price_minor = int(tool_args["min_price"] * 100) if "min_price" in tool_args and tool_args["min_price"] else None
                
                products = CatalogService.search_products(
                    db,
                    query=tool_args.get("query"),
                    category=tool_args.get("category"),
                    max_price_minor=max_price_minor,
                    min_price_minor=min_price_minor,
                    attributes=tool_args.get("attributes")
                )

                # Return clean JSON summary
                results = []
                for p in products:
                    upsell_items = CatalogService.get_upsells(db, p.id)
                    results.append({
                        "id": p.id,
                        "sku": p.sku,
                        "name": p.name,
                        "category": p.category,
                        "description": p.description,
                        "price_rupees": p.price_minor / 100.0,
                        "inventory_qty": p.inventory_qty,
                        "attributes": p.attributes_json,
                        "available_upsells": [{"id": u.id, "name": u.name, "price_rupees": u.price_minor/100.0} for u in upsell_items]
                    })
                
                AuditService.write_audit_event(
                    db, "AGENT", user_id, "SEARCH_PRODUCTS", "PRODUCT", "CATALOG",
                    reason=f"Searched catalog query='{tool_args.get('query')}'", metadata_json=tool_args
                )
                return {"status": "SUCCESS", "count": len(results), "products": results}

            elif tool_name == "get_product":
                p = CatalogService.get_product(db, tool_args["product_id_or_sku"])
                if not p:
                    return {"status": "ERROR", "error": f"Product '{tool_args['product_id_or_sku']}' not found"}
                return {
                    "status": "SUCCESS",
                    "product": {
                        "id": p.id,
                        "sku": p.sku,
                        "name": p.name,
                        "category": p.category,
                        "description": p.description,
                        "price_rupees": p.price_minor / 100.0,
                        "inventory_qty": p.inventory_qty,
                        "attributes": p.attributes_json
                    }
                }

            elif tool_name == "check_inventory":
                avail = CatalogService.check_inventory(db, tool_args["product_id"], tool_args["quantity"])
                return {"status": "SUCCESS", "available": avail}

            elif tool_name == "create_cart":
                cart = CartService.create_cart(db, tool_args.get("user_id", user_id), tool_args.get("merchant_id", "merchant_demo_001"))
                AuditService.write_audit_event(
                    db, "AGENT", user_id, "CREATE_CART", "CART", cart.id,
                    reason="Created new cart", metadata_json={"cart_id": cart.id}
                )
                return {"status": "SUCCESS", "cart_id": cart.id, "version": cart.version, "total_rupees": 0.0}

            elif tool_name == "add_to_cart":
                cart = CartService.add_to_cart(
                    db,
                    cart_id=tool_args["cart_id"],
                    product_id=tool_args["product_id"],
                    quantity=tool_args.get("quantity", 1)
                )
                AuditService.write_audit_event(
                    db, "AGENT", user_id, "ADD_TO_CART", "CART", cart.id,
                    reason=f"Added product {tool_args['product_id']} x {tool_args.get('quantity', 1)}",
                    metadata_json={"cart_id": cart.id, "total_rupees": cart.total_minor / 100.0}
                )
                return {"status": "SUCCESS", "cart_id": cart.id, "total_rupees": cart.total_minor / 100.0, "version": cart.version}

            elif tool_name == "calculate_total":
                total_minor = CartService.recalculate_total(db, tool_args["cart_id"])
                return {"status": "SUCCESS", "cart_id": tool_args["cart_id"], "total_rupees": total_minor / 100.0}

            elif tool_name == "check_policy":
                pol_res = PolicyEngine.evaluate_cart_policy(db, tool_args["cart_id"], tool_args.get("user_id", user_id))
                AuditService.write_audit_event(
                    db, "SYSTEM", user_id, "POLICY_CHECK", "POLICY", tool_args["cart_id"],
                    reason=f"Policy check status: {'PASSED' if pol_res.allowed else 'BLOCKED'}",
                    metadata_json=pol_res.to_dict()
                )
                return {"status": "SUCCESS", "policy_result": pol_res.to_dict()}

            elif tool_name == "request_user_approval":
                cart = CartService.get_cart(db, tool_args["cart_id"])
                if not cart:
                    return {"status": "ERROR", "error": "Cart not found"}
                
                # Check policy first before asking approval
                pol_res = PolicyEngine.evaluate_cart_policy(db, tool_args["cart_id"], tool_args.get("user_id", user_id))
                if not pol_res.allowed:
                    return {"status": "BLOCKED", "policy_error": pol_res.to_dict()}

                # Record pending approval gate
                appr = Approval(
                    cart_id=cart.id,
                    cart_version=cart.version,
                    approved_by=tool_args.get("user_id", user_id),
                    status="APPROVED"  # Auto-approve in agent flow when user confirms
                )
                db.add(appr)
                db.commit()

                AuditService.write_audit_event(
                    db, "USER", user_id, "PAYMENT_APPROVAL", "CART", cart.id,
                    reason=f"Approved purchase summary: {tool_args.get('summary')}",
                    metadata_json={"total_rupees": cart.total_minor / 100.0, "summary": tool_args.get('summary')}
                )
                return {
                    "status": "APPROVED",
                    "cart_id": cart.id,
                    "approved_total_rupees": cart.total_minor / 100.0,
                    "summary": tool_args.get("summary")
                }

            elif tool_name == "create_payment_order":
                cart_id = tool_args["cart_id"]
                uid = tool_args.get("user_id", user_id)

                # Verify policy & approval
                pol_res = PolicyEngine.evaluate_cart_policy(db, cart_id, uid)
                if not pol_res.allowed:
                    return {"status": "BLOCKED_BY_POLICY", "details": pol_res.to_dict()}

                if not PolicyEngine.verify_user_approval(db, cart_id, uid):
                    return {"status": "BLOCKED_NO_APPROVAL", "error": "User approval gate has not been passed for this cart version."}

                cart = CartService.get_cart(db, cart_id)
                # Create DB Order
                order = Order(
                    cart_id=cart_id,
                    user_id=uid,
                    status="CREATED",
                    total_minor=cart.total_minor,
                    currency=cart.currency
                )
                db.add(order)
                db.commit()
                db.refresh(order)

                # Create Razorpay Test Order
                rzp_order = razorpay_adapter.create_order(
                    amount_minor=cart.total_minor,
                    currency=cart.currency,
                    receipt_id=f"rcpt_{order.id[-8:]}"
                )
                order.razorpay_order_id = rzp_order["id"]
                db.commit()

                AuditService.write_audit_event(
                    db, "AGENT", uid, "CREATE_RAZORPAY_ORDER", "ORDER", order.id,
                    reason=f"Created Razorpay order {rzp_order['id']} for INR {order.total_minor/100:.2f}",
                    metadata_json={"razorpay_order_id": rzp_order["id"], "amount_rupees": order.total_minor / 100.0}
                )

                return {
                    "status": "SUCCESS",
                    "order_id": order.id,
                    "razorpay_order_id": rzp_order["id"],
                    "amount_rupees": order.total_minor / 100.0,
                    "currency": order.currency
                }

            elif tool_name == "verify_payment":
                order_id = tool_args["order_id"]
                order = db.query(Order).get(order_id)
                if not order:
                    return {"status": "ERROR", "error": "Order not found"}

                valid = razorpay_adapter.verify_payment_signature(
                    order.razorpay_order_id,
                    tool_args["razorpay_payment_id"],
                    tool_args["razorpay_signature"]
                )

                if valid:
                    order.status = "PAID"
                    payment = Payment(
                        order_id=order.id,
                        razorpay_payment_id=tool_args["razorpay_payment_id"],
                        razorpay_signature=tool_args["razorpay_signature"],
                        status="SUCCESS",
                        amount_minor=order.total_minor
                    )
                    db.add(payment)
                    db.commit()

                    AuditService.write_audit_event(
                        db, "SYSTEM", user_id, "PAYMENT_VERIFIED", "ORDER", order.id,
                        reason="Payment signature verified successfully server-side.",
                        metadata_json={"payment_id": tool_args["razorpay_payment_id"]}
                    )
                    return {"status": "SUCCESS", "order_status": "PAID", "order_id": order.id}
                else:
                    order.status = "PENDING_REVIEW"
                    db.commit()
                    return {"status": "VERIFICATION_FAILED", "order_status": "PENDING_REVIEW"}

            elif tool_name == "simulate_payment_failure_recovery":
                order_id = tool_args["order_id"]
                order = db.query(Order).get(order_id)
                if not order:
                    return {"status": "ERROR", "error": "Order not found"}

                # Trigger simulated failure
                success, fail_info = razorpay_adapter.simulate_payment_attempt(order.razorpay_order_id, force_failure=True)
                order.status = "FAILED"
                payment = Payment(
                    order_id=order.id,
                    razorpay_payment_id=fail_info["razorpay_payment_id"],
                    status="FAILED",
                    amount_minor=order.total_minor,
                    error_code=fail_info["error_code"],
                    error_description=fail_info["error_description"]
                )
                db.add(payment)
                db.commit()

                AuditService.write_audit_event(
                    db, "SYSTEM", user_id, "PAYMENT_FAILED", "ORDER", order.id,
                    reason=f"Controlled test failure: {fail_info['error_description']}",
                    metadata_json=fail_info
                )

                return {
                    "status": "FAILED_HANDLED_GRACEFULLY",
                    "order_id": order.id,
                    "error_description": fail_info["error_description"],
                    "recovery_options": [
                        "Retry with alternate UPI payment method",
                        "Modify cart items / quantities",
                        "Cancel order cleanly without money deduction"
                    ]
                }

            else:
                return {"status": "ERROR", "error": f"Unknown tool: {tool_name}"}

        except Exception as e:
            return {"status": "ERROR", "error": str(e)}
