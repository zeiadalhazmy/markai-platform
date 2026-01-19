import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useAuthStore } from '../stores/auth'
import { supabase } from '../lib/supabase'

vi.mock('../lib/supabase', () => ({
  supabase: {
    auth: {
      signInWithOtp: vi.fn(),
      verifyOtp: vi.fn(),
      signOut: vi.fn(),
      getSession: vi.fn(() => Promise.resolve({ data: { session: null } })),
      onAuthStateChange: vi.fn(),
    }
  }
}))

describe('Auth Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('initializes with null user', () => {
    const auth = useAuthStore()
    expect(auth.user).toBeNull()
  })

  it('signInWithOtp calls supabase', async () => {
    const auth = useAuthStore()
    supabase.auth.signInWithOtp.mockResolvedValue({ error: null })

    await auth.signInWithOtp('test@example.com')

    expect(supabase.auth.signInWithOtp).toHaveBeenCalled()
    expect(auth.loading).toBe(false)
  })
})
