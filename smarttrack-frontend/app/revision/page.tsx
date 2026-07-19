'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

/** Revision Hub is merged into the Learning Center. */
export default function RevisionRedirect() {
  const router = useRouter();
  useEffect(() => {
    router.replace('/learning');
  }, [router]);

  return (
    <div className="min-h-screen bg-[#F8FAFC] flex items-center justify-center text-sm text-[#64748B]">
      Opening Learning Center…
    </div>
  );
}
