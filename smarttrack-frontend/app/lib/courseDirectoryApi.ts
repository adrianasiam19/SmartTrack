import { fetchWithAuth } from './authApi';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export type ProgrammeBrief = {
  slug: string;
  name: string;
  field: string;
  level?: string;
  typical_duration?: string;
  brief: string;
  related_shs_subjects?: string[];
  commonly_offered_at?: string[];
};

export type ProgrammeDetail = ProgrammeBrief & {
  core_topics?: string[];
  career_paths?: string[];
  detailed_overview?: string;
};

export type CourseDirectoryListResponse = {
  count: number;
  fields: string[];
  programmes: ProgrammeBrief[];
  note?: string;
};

export async function listCourseDirectory(params?: {
  field?: string;
  q?: string;
}): Promise<CourseDirectoryListResponse> {
  const sp = new URLSearchParams();
  if (params?.field) sp.set('field', params.field);
  if (params?.q) sp.set('q', params.q);
  const qs = sp.toString();
  const res = await fetchWithAuth(
    `${API_BASE}/course-directory${qs ? `?${qs}` : ''}`,
  );
  if (!res.ok) throw new Error('Failed to load course directory');
  return res.json();
}

export async function getCourseProgramme(slug: string): Promise<ProgrammeDetail> {
  const res = await fetchWithAuth(
    `${API_BASE}/course-directory/${encodeURIComponent(slug)}`,
  );
  if (!res.ok) {
    if (res.status === 404) throw new Error('Programme not found');
    throw new Error('Failed to load programme details');
  }
  return res.json();
}
