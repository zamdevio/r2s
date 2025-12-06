'use server'

// Server Action - intentionally vulnerable to CVE-2025-55182
export async function handleAction(formData: FormData) {
  const action = formData.get('action')
  const input = formData.get('input')
  
  // Simulate some processing
  return {
    success: true,
    action,
    input,
    timestamp: new Date().toISOString(),
    message: `Processed: ${input}`
  }
}

