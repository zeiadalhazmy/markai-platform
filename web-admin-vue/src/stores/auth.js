import { defineStore } from 'pinia'
import { ref } from 'vue'
import { supabase } from '../lib/supabase'

export const useAuthStore = defineStore('auth', () => {
    const user = ref(null)
    const session = ref(null)
    const loading = ref(false)
    const error = ref(null)

    async function signInWithOtp(email) {
        loading.value = true
        error.value = null
        try {
            const { error: err } = await supabase.auth.signInWithOtp({
                email,
                options: {
                    shouldCreateUser: false, // Only allow existing users? Modify based on logic
                }
            })
            if (err) throw err
        } catch (e) {
            error.value = e.message
        } finally {
            loading.value = false
        }
    }

    async function verifyOtp(email, token) {
        loading.value = true
        error.value = null
        try {
            const { data, error: err } = await supabase.auth.verifyOtp({
                email,
                token,
                type: 'email'
            })
            if (err) throw err
            user.value = data.user
            session.value = data.session
            return true
        } catch (e) {
            error.value = e.message
            return false
        } finally {
            loading.value = false
        }
    }

    async function signOut() {
        await supabase.auth.signOut()
        user.value = null
        session.value = null
    }

    // Initialize
    async function init() {
        const { data } = await supabase.auth.getSession()
        session.value = data.session
        user.value = data.session?.user ?? null

        supabase.auth.onAuthStateChange((_event, _session) => {
            session.value = _session
            user.value = _session?.user ?? null
        })
    }

    return { user, session, loading, error, signInWithOtp, verifyOtp, signOut, init }
})
