import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  const isWarRoom = request.nextUrl.pathname.startsWith('/war-room');
  
  if (isWarRoom) {
    const session = request.cookies.get('af_session')?.value;
    
    // Check if the URL already has a paranoia query param to force UI state
    // Or if the session is missing
    const isPublic = !session && request.nextUrl.searchParams.get('auth') !== 'true';

    const requestHeaders = new Headers(request.headers);
    requestHeaders.set('x-is-public', isPublic ? 'true' : 'false');

    return NextResponse.next({
      request: {
        headers: requestHeaders,
      },
    });
  }

  return NextResponse.next();
}

export const config = {
  matcher: ['/war-room/:path*'],
};
