from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.conf import settings

import razorpay


from .models import (
    Category,
    Product,
    Supplier,
    SupplierProduct,   # 🔥 YE LINE ADD KARO
    Feedback,
    Order,
    OrderItem
)

# ======================================================
# 🔥 RAZORPAY CLIENT (GLOBAL)
# ======================================================
client = razorpay.Client(
    auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
)

# ======================
# AUTHS(LOGIN, REGISTER)
# ======================
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
import json


def auth_page(request):
    return render(request, "login.html")


@csrf_exempt
def register_user(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request"}, status=400)

    data = json.loads(request.body)
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if User.objects.filter(username=username).exists():
        return JsonResponse({"error": "Username already exists"}, status=400)

    User.objects.create_user(
        username=username,
        email=email,
        password=password
    )
    return JsonResponse({"success": True})


@csrf_exempt
def login_user(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request"}, status=400)

    data = json.loads(request.body)
    username = data.get("username")
    password = data.get("password")

    user = authenticate(username=username, password=password)
    if user is None:
        return JsonResponse({"error": "Invalid credentials"}, status=401)

    login(request, user)
    return JsonResponse({"success": True})

# ======================
# DASHBOARD
# ======================
from django.shortcuts import render, redirect
from shop.models import Feedback

def dashboard(request):
    # optional: login required
    # if not request.user.is_authenticated:
    #     return redirect("login")

    testimonials = Feedback.objects.filter(
        is_visible=True
    ).order_by("-created_at")[:6]

    return render(request, "dashboard.html", {
        "testimonials": testimonials
    })

def logout_user(request):
    logout(request)
    return redirect("dashboard")

# ======================
# CATEGORIES
# ======================
def categories(request):
    return render(
        request,
        "categories.html",
        {"categories": Category.objects.all()}
    )


# ======================
# PRODUCTS
# ======================
from .models import Product, Category

def products(request):
    category_name = request.GET.get("category")

    products = Product.objects.all()

    if category_name:
        products = products.filter(category__name=category_name)

    return render(request, "product.html", {
        "products": products,
        "categories": Category.objects.all(),
        "selected_category": category_name
    })
# ======================
# SEARCH SUGGESTIONS
# ======================

from django.http import JsonResponse
from .models import Product

def product_search_suggestions(request):
    q = request.GET.get("q","")

    products = Product.objects.filter(
        name__icontains=q
    )[:6]

    data = []
    for p in products:
        data.append({
            "id": p.id,
            "name": p.name,
            "price": p.price,
            "image": p.image.url if p.image else ""
        })

    return JsonResponse({"results": data})

# ======================
# SUPPLIER REGISTER
# ======================
from django.http import JsonResponse
from django.contrib.auth.hashers import make_password
from .models import Supplier

def supplier_register(request):
    if request.method == "POST":

        email = request.POST.get("email")

        if Supplier.objects.filter(email=email).exists():
            return JsonResponse({
                "status": "error",
                "message": "Email already registered"
            })

        Supplier.objects.create(
            company_name=request.POST.get("company"),
            owner_name=request.POST.get("owner_name"),
            email=email,
            phone=request.POST.get("phone"),
            address=request.POST.get("address"),
            password=make_password(request.POST.get("password"))
        )

        return JsonResponse({"status": "success"})

    return render(request, "supplier_register.html")


# ======================
# SUPPLIER LOGIN
# ======================
# shop/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Supplier
from django.contrib.auth.hashers import check_password


from django.http import JsonResponse
from django.contrib.auth.hashers import check_password
from .models import Supplier

def supplier_login(request):
    if request.method == "POST":
        owner_name = request.POST.get("owner_name")
        password = request.POST.get("password")

        try:
            supplier = Supplier.objects.get(owner_name=owner_name)

            if check_password(password, supplier.password):
                request.session["supplier_id"] = supplier.id
                return JsonResponse({"status": "success"})
            else:
                return JsonResponse({
                    "status": "error",
                    "message": "Invalid password"
                })

        except Supplier.DoesNotExist:
            return JsonResponse({"status": "not_registered"})

    return render(request, "supplier_login.html")

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from .models import Supplier


def supplier_forgot_password(request):
    if request.method == "POST":
        owner_name = request.POST.get("owner_name")
        new_password = request.POST.get("new_password")

        try:
            supplier = Supplier.objects.get(owner_name=owner_name)
            supplier.password = make_password(new_password)
            supplier.save()

            messages.success(request, "Password reset successful. Please login.")
            return redirect("supplier_login")

        except Supplier.DoesNotExist:
            messages.error(request, "Supplier not found")

    return render(request, "supplier_forgot_password.html")

# ======================
# SUPPLIER DASHBOARD
# ======================
from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Q
from .models import SupplierProduct, Supplier


def supplier_dashboard(request):
    supplier_id = request.session.get("supplier_id")
    supplier = Supplier.objects.get(id=supplier_id)

    q = request.GET.get("q", "")

    approved_products = SupplierProduct.objects.filter(
        supplier=supplier,
        is_approved=True
    )

    if q:
        approved_products = approved_products.filter(
            Q(name__icontains=q) |
            Q(category__name__icontains=q)
        )

    pending_products = SupplierProduct.objects.filter(
        supplier=supplier,
        is_approved=False
    )

    live_products = SupplierProduct.objects.filter(
        supplier=supplier,
        is_approved=True,
        is_published=True
    )

    return render(request, "supplier_dashboard.html", {
        "supplier": supplier,
        "approved_products": approved_products,
        "pending_products": pending_products,
        "live_products": live_products,
    })


# 🔍 LIVE SEARCH SUGGESTIONS (WITH IMAGE)
def supplier_product_suggestions(request):
    supplier_id = request.session.get("supplier_id")
    q = request.GET.get("q", "")

    if not supplier_id or not q:
        return JsonResponse({"results": []})

    products = SupplierProduct.objects.filter(
        supplier_id=supplier_id,
        name__icontains=q
    )[:6]

    data = []
    for p in products:
        data.append({
            "id": p.id,
            "name": p.name,
            "price": p.price,
            "image": p.image.url if p.image else ""
        })

    return JsonResponse({"results": data})



from django.shortcuts import render, get_object_or_404
from .models import SupplierProduct, Supplier

def supplier_product_detail(request, pk):
    supplier_id = request.session.get("supplier_id")
    supplier = get_object_or_404(Supplier, id=supplier_id)

    product = get_object_or_404(
        SupplierProduct,
        id=pk,
        supplier=supplier
    )

    return render(request, "supplier_product_detail.html", {
        "supplier": supplier,
        "product": product
    })


def supplier_logout(request):
    request.session.flush()
    return redirect("dashboard")

from .models import Supplier, Product, Category, SupplierProduct

from .models import SupplierProduct, Category

def supplier_add_product(request):
    supplier_id = request.session.get("supplier_id")
    if not supplier_id:
        return redirect("supplier_login")

    supplier = Supplier.objects.get(id=supplier_id)

    if request.method == "POST":
        SupplierProduct.objects.create(
            supplier=supplier,
            name=request.POST["name"],
            category_id=request.POST["category"],
            price=request.POST["price"],
            stock=request.POST["stock"],
            image=request.FILES["image"],
            is_approved=False   # ⛔ admin approve karega
        )

        messages.success(request, "Product sent for admin approval")
        return redirect("supplier_dashboard")

    return render(request, "supplier_add_product.html", {
        "categories": Category.objects.all()
    })


# ======================
# ADD PRODUCT (ADMIN / SUPPLIER)
# ======================
@login_required
def add_product(request):
    if request.method == "POST":
        Product.objects.create(
            name=request.POST["name"],
            category_id=request.POST["category"],
            price=request.POST["price"],
            stock=request.POST["stock"],
            image=request.FILES.get("image")
        )

        return JsonResponse({"success": True})

    return render(request, "add_product.html", {
        "categories": Category.objects.all()
    })

# ======================
# SUPPLIER DASHBOARD PRODUCT PUBLISH
# ======================


from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import SupplierProduct, Product

def publish_product(request, id):
    if not request.session.get("supplier_id"):
        return redirect("supplier_login")

    supplier_id = request.session["supplier_id"]
    sp = get_object_or_404(
        SupplierProduct,
        id=id,
        supplier_id=supplier_id,
        is_approved=True,
        is_published=False
    )

    # ✅ COPY TO MAIN PRODUCT TABLE
    Product.objects.create(
        name=sp.name,
        price=sp.price,
        stock=sp.stock,
        category=sp.category,
        image=sp.image
    )

    # ✅ MARK AS PUBLISHED
    sp.is_published = True
    sp.save()

    messages.success(request, "Product published successfully!")
    return redirect("supplier_dashboard")

# ======================
# CART (AJAX)
# ======================
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if product.stock < 1:
        return JsonResponse({"error": "Out of stock"}, status=400)

    cart = request.session.get("cart", {})
    cart[str(product_id)] = cart.get(str(product_id), 0) + 1
    request.session["cart"] = cart

    return JsonResponse({
        "success": True,
        "cart_count": sum(cart.values())
    })


def cart_view(request):
    cart = request.session.get("cart", {})
    products = Product.objects.filter(id__in=cart.keys())

    cart_items = []
    total = 0

    for p in products:
        qty = cart[str(p.id)]
        subtotal = p.price * qty
        total += subtotal

        cart_items.append({
            "product": p,
            "qty": qty,
            "subtotal": subtotal
        })

    return render(request, "cart.html", {
        "cart_items": cart_items,
        "total": total
    })


def remove_from_cart(request, product_id):
    cart = request.session.get("cart", {})
    cart.pop(str(product_id), None)
    request.session["cart"] = cart
    return redirect("cart")


# ======================
# CHECKOUT (COD + RAZORPAY)
# ======================
from decimal import Decimal
from django.conf import settings

def checkout(request):
    cart = request.session.get("cart", {})
    products = Product.objects.filter(id__in=cart.keys())

    total = Decimal("0")
    for p in products:
        total += p.price * cart[str(p.id)]

    total_int = int(total)
    razorpay_amount = total_int * 100

    if request.method == "POST":
        method = request.POST.get("payment_method")

        request.session["checkout_name"] = request.POST["name"]
        request.session["checkout_phone"] = request.POST["phone"]
        request.session["checkout_address"] = request.POST["address"]
        request.session["order_total"] = float(total)

        # ---------- COD ----------
        if method == "COD":
            order = Order.objects.create(
                user=request.user if request.user.is_authenticated else None,
                customer_name=request.POST["name"],
                phone=request.POST["phone"],
                address=request.POST["address"],
                total_amount=total,
                payment_method="COD"
            )

            for p in products:
                OrderItem.objects.create(
                    order=order,
                    product=p,
                    quantity=cart[str(p.id)],
                    price=p.price
                )
                p.stock -= cart[str(p.id)]
                p.save()

            request.session["cart"] = {}
            return redirect("order_success", order.id)

        # ---------- RAZORPAY ----------
        rp_order = client.order.create({
            "amount": razorpay_amount,
            "currency": "INR",
            "payment_capture": 1
        })

        request.session["rp_order"] = {
            "id": rp_order["id"],
            "amount_paise": razorpay_amount,
            "amount_rupees": float(total)
        }

        return render(request, "razorpay.html", {
            "razorpay_key": settings.RAZORPAY_KEY_ID,
            "order_id": rp_order["id"],
            "amount": razorpay_amount,
            "total": total
        })

    return render(request, "checkout.html", {"total": total})



# ======================
# RAZORPAY SUCCESS
# ======================

from decimal import Decimal
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def razorpay_success(request):
    if request.method == "POST":
        payment_id = request.POST.get("razorpay_payment_id")

        cart = request.session.get("cart", {})
        products = Product.objects.filter(id__in=cart.keys())

        total = Decimal(str(request.session.get("order_total")))

        # ✅ ORDER CREATE (MODEL KE HISAAB SE)
        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            customer_name=request.session.get("checkout_name"),
            phone=request.session.get("checkout_phone"),
            address=request.session.get("checkout_address"),
            total_amount=total,
            payment_method="RAZORPAY",
            payment_id=payment_id,      # ✅ Razorpay payment id
            status="PLACED"             # ✅ default status
        )

        # ✅ ORDER ITEMS
        for p in products:
            OrderItem.objects.create(
                order=order,
                product=p,
                quantity=cart[str(p.id)],
                price=p.price
            )
            p.stock -= cart[str(p.id)]
            p.save()

        # ✅ CART CLEAR
        request.session["cart"] = {}

        return redirect("order_success", order.id)

# ======================
# ORDERS
# ======================

from django.db.models import Q

def my_orders(request):
    # Case 1: Logged in user
    if request.user.is_authenticated:
        orders = Order.objects.filter(user=request.user)

    # Case 2: Guest user (phone based)
    else:
        phone = request.session.get("checkout_phone")
        if not phone:
            orders = Order.objects.none()
        else:
            orders = Order.objects.filter(phone=phone)

    orders = orders.order_by("-created_at")

    return render(request, "my_orders.html", {"orders": orders})


def order_success(request, id):
    return render(
        request,
        "order_success.html",
        {"order": get_object_or_404(Order, id=id)}
    )

# ======================
# PRODUCT DETAIL PAGE
# ======================

from django.shortcuts import render, get_object_or_404, redirect
from .models import Product

def product_detail(request, pk):
    product = get_object_or_404(Product, id=pk)

    return render(request, "product_detail.html", {
        "product": product
    })
# ======================
# BUY NOW WORK
# ======================

def buy_now(request, pk):
    product = get_object_or_404(Product, id=pk)

    cart = request.session.get("cart", {})
    cart[str(product.id)] = 1
    request.session["cart"] = cart

    return redirect("checkout")

# ======================
# AUTH
# ======================
def login_view(request):
    if request.method == "POST":
        user = authenticate(
            request,
            username=request.POST["username"],
            password=request.POST["password"]
        )
        if user:
            login(request, user)
            return redirect("dashboard")

        return render(request, "login.html", {"error": "Invalid credentials"})

    return render(request, "login.html")


def logout_view(request):
    logout(request)
    return redirect("dashboard")


# ======================
# INVOICE DOWNLOAD
# ======================

from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch

def download_invoice(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="Invoice_{order.id}.pdf"'

    doc = SimpleDocTemplate(
        response,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()
    elements = []

    # HEADER
    elements.append(
        Paragraph(
            "<b><font size=18>HardwarePro</font></b><br/>Professional Hardware Solutions",
            styles["Title"]
        )
    )
    elements.append(Spacer(1, 20))

    elements.append(
        Paragraph(
            f"""
            <b>Invoice ID:</b> #{order.id}<br/>
            <b>Customer:</b> {order.customer_name}<br/>
            <b>Phone:</b> {order.phone}<br/>
            <b>Address:</b> {order.address}<br/><br/>
            <b>Payment:</b> {order.payment_method}<br/>
            <b>Date:</b> {order.created_at.strftime('%d %b %Y')}
            """,
            styles["Normal"]
        )
    )

    elements.append(Spacer(1, 20))

    # TABLE
    data = [["Product", "Qty", "Price", "Subtotal"]]
    total = 0

    for item in order.items.all():
        subtotal = item.quantity * item.price
        total += subtotal
        data.append([
            item.product.name,
            item.quantity,
            f"₹ {item.price}",
            f"₹ {subtotal}"
        ])

    data.append(["", "", "Total", f"₹ {total}"])

    table = Table(data, colWidths=[3.5*inch, 1*inch, 1.2*inch, 1.2*inch])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#0d6efd")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTNAME", (0,-1), (-1,-1), "Helvetica-Bold"),
        ("BACKGROUND", (0,-1), (-1,-1), colors.lightgrey),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 30))

    elements.append(
        Paragraph(
            "<i>Thank you for shopping with HardwarePro</i>",
            ParagraphStyle(name="Footer", alignment=1, fontSize=10)
        )
    )

    doc.build(elements)
    return response


# ======================
# UPDATE SUPPLY REQUEST
# ======================
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required

@login_required
def update_supply_request(request, request_id, action):
    req = get_object_or_404(SupplyRequest, id=request_id)

    # security: sirf apna supplier hi update kare
    if req.supplier != request.user.supplier:
        return redirect("supplier_dashboard")

    if action == "accept":
        req.status = "ACCEPTED"
        req.product.stock += req.quantity
        req.product.save()

    elif action == "reject":
        req.status = "REJECTED"

    req.save()
    return redirect("supplier_dashboard")

# ======================
# SERVICE PAGE
# ======================

from django.shortcuts import render
from .models import Product, Category

def services(request):
    products = Product.objects.all()
    categories = Category.objects.all()

    return render(request, "services.html", {
        "products": products,
        "categories": categories
    })

# ======================
# FEEDBACK
# ======================

from django.shortcuts import render, redirect
from .models import Feedback

def feedback(request):
    if request.method == "POST":

        role = request.POST.get("role")
        name = request.POST.get("name")
        message = request.POST.get("message")
        rating = request.POST.get("rating", 5)

        Feedback.objects.create(
            user=request.user if request.user.is_authenticated else None,
            role=role,
            name=name,
            message=message,
            rating=int(rating),
        )

        return redirect("feedback_success")   #  success page

    return render(request, "feedback.html")



def feedback_success(request):
    return render(request, "feedback_success.html")

# ======================
# ABOUTUS
# ======================

from django.shortcuts import render, redirect
from .models import ContactMessage   # agar contact data store karna hai

def about(request):
    return render(request, "about.html")


# ======================
# CONTACT US
# ======================

from django.contrib import messages
from django.shortcuts import render, redirect
from .models import ContactMessage

def contact(request):
    if request.method == "POST":
        ContactMessage.objects.create(
            name=request.POST["name"],
            email=request.POST["email"],
            message=request.POST["message"]
        )
        messages.success(request, "✅ Thank you! Your message has been sent successfully.")
        return redirect("contact")

    return render(request, "contact.html")

# ======================
# POLICY PAGES
# ======================


from django.shortcuts import render

def privacy_policy(request):
    return render(request, "policy/privacy_policy.html")

def terms(request):
    return render(request, "policy/terms.html")

def refund_policy(request):
    return render(request, "policy/refund_policy.html")

def shipping_policy(request):
    return render(request, "policy/shipping_policy.html")

def cookie_policy(request):
    return render(request, "policy/cookie_policy.html")
