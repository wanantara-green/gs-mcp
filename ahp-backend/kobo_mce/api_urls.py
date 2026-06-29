"""api_urls.py — Routing endpoint API kobo_mce."""
from django.urls import path
from . import views

urlpatterns = [
    path("submit/", views.submit_response, name="submit"),
    path("experts/", views.list_experts, name="experts"),
    path("experts/<str:expert_id>/", views.expert_detail, name="expert-detail"),
    path("weights/", views.compute_weights, name="weights"),
    path("validate/", views.validate_only, name="validate"),
    path("narrative/", views.narrative, name="narrative"),
    # ── Operasi tulis admin (wajib sandi via body 'admin_token') ──
    path("admin/verify/", views.admin_verify, name="admin-verify"),
    path("admin/save/", views.admin_save, name="admin-save"),
    path("admin/delete/", views.admin_delete, name="admin-delete"),
]
