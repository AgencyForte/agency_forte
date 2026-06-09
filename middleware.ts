import { NextRequest, NextResponse } from "next/server";

export function middleware(request: NextRequest) {
  const passwordConfigured = Boolean(process.env.INSURETRA_ADMIN_PASSWORD);
  const isAdminPath = request.nextUrl.pathname.startsWith("/admin");
  const isLoginPath = request.nextUrl.pathname.startsWith("/admin/login");

  if (!isAdminPath || isLoginPath || !passwordConfigured) {
    return NextResponse.next();
  }

  const authenticated = request.cookies.get("insuretra_admin")?.value === "1";
  if (authenticated) {
    return NextResponse.next();
  }

  const loginUrl = request.nextUrl.clone();
  loginUrl.pathname = "/admin/login";
  loginUrl.searchParams.set("next", request.nextUrl.pathname);
  return NextResponse.redirect(loginUrl);
}

export const config = {
  matcher: ["/admin/:path*"]
};
