from pathlib import Path


def test_no_public_seo_routes_exist():
    app_dir = Path("app")
    forbidden = {"sitemap.ts", "robots.ts", "profiles", "agencies"}
    existing = {path.name for path in app_dir.rglob("*") if path.name in forbidden}

    assert existing == set()


def test_admin_routes_exist():
    for route in [
        "app/admin/pipeline-runs/page.tsx",
        "app/admin/events/page.tsx",
        "app/admin/suppressed-severances/page.tsx",
        "app/admin/anomalies/page.tsx",
    ]:
        assert Path(route).exists()

