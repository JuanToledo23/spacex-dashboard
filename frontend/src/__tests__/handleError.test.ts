import { describe, it, expect } from 'vitest'
import axios, { AxiosError, AxiosHeaders } from 'axios'
import { extractErrorMessage } from '@/utils/handleError'

describe('extractErrorMessage', () => {
  it('returns fallback for plain Error', () => {
    const result = extractErrorMessage(new Error('oops'), 'Something went wrong')
    expect(result).toBe('Something went wrong')
  })

  it('returns fallback for unknown values', () => {
    expect(extractErrorMessage(null, 'fallback')).toBe('fallback')
    expect(extractErrorMessage(undefined, 'fallback')).toBe('fallback')
    expect(extractErrorMessage(42, 'fallback')).toBe('fallback')
  })

  it('returns fallback for string errors', () => {
    expect(extractErrorMessage('a string error', 'fallback')).toBe('fallback')
  })

  it('returns server message for AxiosError with response data', () => {
    const err = new AxiosError(
      'Request failed',
      'ERR_BAD_REQUEST',
      undefined,
      undefined,
      {
        status: 400,
        statusText: 'Bad Request',
        headers: {},
        config: { headers: new AxiosHeaders() },
        data: { message: 'Validation failed' },
      },
    )
    expect(axios.isAxiosError(err)).toBe(true)
    const result = extractErrorMessage(err, 'fallback')
    expect(result).toBe('Validation failed')
  })

  it('returns fallback for AxiosError without response data message', () => {
    const err = new AxiosError(
      'Request failed',
      'ERR_BAD_REQUEST',
      undefined,
      undefined,
      {
        status: 500,
        statusText: 'Server Error',
        headers: {},
        config: { headers: new AxiosHeaders() },
        data: {},
      },
    )
    const result = extractErrorMessage(err, 'fallback')
    expect(result).toBe('fallback')
  })

  it('returns fallback for AxiosError without response', () => {
    const err = new AxiosError('Network Error', 'ERR_NETWORK')
    const result = extractErrorMessage(err, 'net fallback')
    expect(result).toBe('net fallback')
  })
})
