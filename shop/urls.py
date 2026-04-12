from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),

    path("categories/", views.categories, name="categories"),
    path("products/", views.products, name="products"),

    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),

    path("feedback/", views.feedback, name="feedback"),

    path("login/", views.auth_page, name="login"),
    path("auth/register/", views.register_user, name="register_user"),
    path("auth/login/", views.login_user, name="login_user"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("logout/", views.logout_user, name="logout"),
    path("services/", views.services, name="services"),
    # =========================
    # HTML SUPPORT (FRONTEND FIX)
    # =========================
    path("dashboard.html", views.dashboard),
    path("categories.html", views.categories),
    path("product.html", views.products),
    path("product.html", views.products),
    path("feedback.html", views.feedback),

    # =========================
    # PRODUCT / CART
    # =========================
    path("add-product/", views.add_product, name="add_product"),
    path("add-product.html", views.add_product),

    path("add-to-cart/<int:product_id>/", views.add_to_cart, name="add_to_cart"),
    path("cart/", views.cart_view, name="cart"),
    path("remove-from-cart/<int:product_id>/", views.remove_from_cart, name="remove_from_cart"),

    # =========================
    # CHECKOUT / PAYMENT
    # =========================
    path("checkout/", views.checkout, name="checkout"),
    path("razorpay-success/", views.razorpay_success, name="razorpay_success"),

    path("order-success/<int:id>/", views.order_success, name="order_success"),

    # =========================
    # ORDERS
    # =========================
    path("my-orders/", views.my_orders, name="my_orders"),
    path("invoice/<int:order_id>/", views.download_invoice, name="download_invoice"),
    # ---------- SUPPLIER AUTH ----------
    path("supplier/register/", views.supplier_register, name="supplier_register"),
    path("supplier/login/", views.supplier_login, name="supplier_login"),
    path("supplier/logout/", views.supplier_logout, name="supplier_logout"),
    path("supplier/forgot-password/", views.supplier_forgot_password, name="supplier_forgot_password"),

    # ---------- SUPPLIER DASHBOARD ----------
    path("supplier/dashboard/", views.supplier_dashboard, name="supplier_dashboard"),

    # ---------- SUPPLIER PRODUCT ----------
    path("supplier/add-product/", views.supplier_add_product, name="supplier_add_product"),   # ---------- SUPPLIER AUTH ----------
    path("supplier/register/", views.supplier_register, name="supplier_register"),
    path("supplier/login/", views.supplier_login, name="supplier_login"),
    path("supplier/logout/", views.supplier_logout, name="supplier_logout"),
    path("supplier/forgot-password/", views.supplier_forgot_password, name="supplier_forgot_password"),

    # ---------- SUPPLIER DASHBOARD ----------
    path("supplier/dashboard/", views.supplier_dashboard, name="supplier_dashboard"),

    # ---------- SUPPLIER PRODUCT ----------
    path("supplier/add-product/", views.supplier_add_product, name="supplier_add_product"),
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),
# POLICY PAGES
    path("privacy-policy/", views.privacy_policy, name="privacy_policy"),
    path("terms/", views.terms, name="terms"),
    path("refund-policy/", views.refund_policy, name="refund_policy"),
    path("shipping-policy/", views.shipping_policy, name="shipping_policy"),
    path("cookie-policy/", views.cookie_policy, name="cookie_policy"),
    path("supplier/publish/<int:id>/", views.publish_product, name="publish_product"),
    path("product/<int:pk>/", views.product_detail, name="product_detail"),
    path("buy-now/<int:pk>/", views.buy_now, name="buy_now"),
    path( "supplier/search-suggestions/",  views.supplier_product_suggestions,  name="supplier_product_suggestions"),
    path("products/search-suggestions/", views.product_search_suggestions, name="product_search_suggestions"),
    path("product/<int:pk>/", views.supplier_product_detail, name="supplier_product_detail"),

    path("feedback/", views.feedback, name="feedback"),
    path("feedback/success/", views.feedback_success, name="feedback_success"),
]
