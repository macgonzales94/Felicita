/**
 * HOOK useApi - PROYECTO FELICITA
 * Sistema de Facturación Electrónica para Perú
 * 
 * Hook personalizado para manejo de llamadas a API con estados de carga
 */

import { useState, useEffect, useCallback, useRef } from 'react'
import { toast } from 'react-hot-toast'

// =============================================================================
// TIPOS E INTERFACES
// =============================================================================

export interface UseApiState<T> {
  data: T | null
  loading: boolean
  error: string | null
  success: boolean
}

export interface UseApiOptions {
  immediate?: boolean
  showToasts?: boolean
  onSuccess?: (data: any) => void
  onError?: (error: string) => void
  retryCount?: number
  retryDelay?: number
}

export interface UseMutationOptions<TData, TVariables> extends UseApiOptions {
  onSuccess?: (data: TData, variables: TVariables) => void
  onError?: (error: string, variables: TVariables) => void
}

export interface UseQueryOptions<TData> extends UseApiOptions {
  dependencies?: any[]
  refetchInterval?: number
  staleTime?: number
  enabled?: boolean
}

// =============================================================================
// HOOK BASE useApi
// =============================================================================

/**
 * Hook base para llamadas a API
 */
export function useApi<T>(
  apiFunction: () => Promise<T>,
  options: UseApiOptions = {}
) {
  const {
    immediate = false,
    showToasts = true,
    onSuccess,
    onError,
    retryCount = 0,
    retryDelay = 1000
  } = options

  const [state, setState] = useState<UseApiState<T>>({
    data: null,
    loading: false,
    error: null,
    success: false
  })

  const mountedRef = useRef(true)
  const retryTimeoutRef = useRef<NodeJS.Timeout>()

  // Función para ejecutar la API
  const execute = useCallback(async (attempt = 0): Promise<T | null> => {
    if (!mountedRef.current) return null

    setState(prev => ({ 
      ...prev, 
      loading: true, 
      error: null, 
      success: false 
    }))

    try {
      const result = await apiFunction()
      
      if (!mountedRef.current) return null

      setState({
        data: result,
        loading: false,
        error: null,
        success: true
      })

      if (showToasts) {
        toast.success('Operación exitosa')
      }

      onSuccess?.(result)
      return result

    } catch (error: any) {
      if (!mountedRef.current) return null

      const errorMessage = error?.response?.data?.message || 
                          error?.message || 
                          'Error inesperado'

      // Retry logic
      if (attempt < retryCount) {
        retryTimeoutRef.current = setTimeout(() => {
          execute(attempt + 1)
        }, retryDelay * Math.pow(2, attempt)) // Exponential backoff
        return null
      }

      setState({
        data: null,
        loading: false,
        error: errorMessage,
        success: false
      })

      if (showToasts) {
        toast.error(errorMessage)
      }

      onError?.(errorMessage)
      return null
    }
  }, [apiFunction, onSuccess, onError, showToasts, retryCount, retryDelay])

  // Reset function
  const reset = useCallback(() => {
    setState({
      data: null,
      loading: false,
      error: null,
      success: false
    })
  }, [])

  // Cleanup
  useEffect(() => {
    return () => {
      mountedRef.current = false
      if (retryTimeoutRef.current) {
        clearTimeout(retryTimeoutRef.current)
      }
    }
  }, [])

  // Execute immediately if requested
  useEffect(() => {
    if (immediate) {
      execute()
    }
  }, [immediate, execute])

  return {
    ...state,
    execute,
    reset,
    refetch: execute
  }
}

// =============================================================================
// HOOK useQuery
// =============================================================================

/**
 * Hook para queries con cache y refetch automático
 */
export function useQuery<TData>(
  queryKey: string,
  queryFunction: () => Promise<TData>,
  options: UseQueryOptions<TData> = {}
) {
  const {
    dependencies = [],
    refetchInterval,
    staleTime = 5 * 60 * 1000, // 5 minutos
    enabled = true,
    ...apiOptions
  } = options

  const cacheRef = useRef<Map<string, { data: any; timestamp: number }>>(new Map())
  const intervalRef = useRef<NodeJS.Timeout>()

  // Función de query con cache
  const cachedQueryFunction = useCallback(async (): Promise<TData> => {
    const now = Date.now()
    const cached = cacheRef.current.get(queryKey)
    
    // Retornar cache si es válido
    if (cached && (now - cached.timestamp) < staleTime) {
      return cached.data
    }

    // Ejecutar query y actualizar cache
    const result = await queryFunction()
    cacheRef.current.set(queryKey, { data: result, timestamp: now })
    
    return result
  }, [queryKey, queryFunction, staleTime])

  const apiResult = useApi(cachedQueryFunction, {
    immediate: enabled,
    ...apiOptions
  })

  // Refetch automático
  useEffect(() => {
    if (refetchInterval && enabled) {
      intervalRef.current = setInterval(() => {
        apiResult.refetch()
      }, refetchInterval)

      return () => {
        if (intervalRef.current) {
          clearInterval(intervalRef.current)
        }
      }
    }
  }, [refetchInterval, enabled, apiResult.refetch])

  // Refetch cuando cambien dependencias
  useEffect(() => {
    if (enabled) {
      apiResult.refetch()
    }
  }, [...dependencies, enabled])

  // Invalidar cache
  const invalidateCache = useCallback(() => {
    cacheRef.current.delete(queryKey)
  }, [queryKey])

  return {
    ...apiResult,
    invalidateCache
  }
}

// =============================================================================
// HOOK useMutation
// =============================================================================

/**
 * Hook para mutaciones (POST, PUT, DELETE)
 */
export function useMutation<TData, TVariables = void>(
  mutationFunction: (variables: TVariables) => Promise<TData>,
  options: UseMutationOptions<TData, TVariables> = {}
) {
  const {
    onSuccess,
    onError,
    showToasts = true,
    ...apiOptions
  } = options

  const [state, setState] = useState<UseApiState<TData> & { variables: TVariables | null }>({
    data: null,
    loading: false,
    error: null,
    success: false,
    variables: null
  })

  const mountedRef = useRef(true)

  // Función mutate
  const mutate = useCallback(async (variables: TVariables): Promise<TData | null> => {
    if (!mountedRef.current) return null

    setState(prev => ({
      ...prev,
      loading: true,
      error: null,
      success: false,
      variables
    }))

    try {
      const result = await mutationFunction(variables)
      
      if (!mountedRef.current) return null

      setState(prev => ({
        ...prev,
        data: result,
        loading: false,
        error: null,
        success: true
      }))

      if (showToasts) {
        toast.success('Operación exitosa')
      }

      onSuccess?.(result, variables)
      return result

    } catch (error: any) {
      if (!mountedRef.current) return null

      const errorMessage = error?.response?.data?.message || 
                          error?.message || 
                          'Error inesperado'

      setState(prev => ({
        ...prev,
        data: null,
        loading: false,
        error: errorMessage,
        success: false
      }))

      if (showToasts) {
        toast.error(errorMessage)
      }

      onError?.(errorMessage, variables)
      return null
    }
  }, [mutationFunction, onSuccess, onError, showToasts])

  // Reset function
  const reset = useCallback(() => {
    setState({
      data: null,
      loading: false,
      error: null,
      success: false,
      variables: null
    })
  }, [])

  // Cleanup
  useEffect(() => {
    return () => {
      mountedRef.current = false
    }
  }, [])

  return {
    ...state,
    mutate,
    reset
  }
}

// =============================================================================
// HOOK useInfiniteQuery
// =============================================================================

/**
 * Hook para queries con scroll infinito
 */
export function useInfiniteQuery<TData>(
  queryKey: string,
  queryFunction: (page: number) => Promise<{ data: TData[]; hasMore: boolean }>,
  options: UseQueryOptions<TData[]> = {}
) {
  const [allData, setAllData] = useState<TData[]>([])
  const [page, setPage] = useState(1)
  const [hasMore, setHasMore] = useState(true)
  
  const queryWithPage = useCallback(async () => {
    const result = await queryFunction(page)
    return result
  }, [queryFunction, page])

  const { data, loading, error, execute } = useApi(queryWithPage, {
    immediate: false,
    ...options
  })

  // Cargar siguiente página
  const loadMore = useCallback(() => {
    if (!loading && hasMore) {
      setPage(prev => prev + 1)
    }
  }, [loading, hasMore])

  // Reset
  const reset = useCallback(() => {
    setAllData([])
    setPage(1)
    setHasMore(true)
  }, [])

  // Ejecutar query cuando cambie la página
  useEffect(() => {
    execute()
  }, [page, execute])

  // Actualizar datos cuando llegue respuesta
  useEffect(() => {
    if (data) {
      if (page === 1) {
        setAllData(data.data)
      } else {
        setAllData(prev => [...prev, ...data.data])
      }
      setHasMore(data.hasMore)
    }
  }, [data, page])

  return {
    data: allData,
    loading,
    error,
    hasMore,
    loadMore,
    reset,
    refetch: () => {
      reset()
      execute()
    }
  }
}

// =============================================================================
// HOOKS ESPECÍFICOS PARA FELICITA
// =============================================================================

/**
 * Hook para búsqueda con debounce
 */
export function useSearch<TData>(
  searchFunction: (query: string) => Promise<TData[]>,
  debounceMs = 300
) {
  const [query, setQuery] = useState('')
  const [debouncedQuery, setDebouncedQuery] = useState('')
  const timeoutRef = useRef<NodeJS.Timeout>()

  // Debounce del query
  useEffect(() => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current)
    }

    timeoutRef.current = setTimeout(() => {
      setDebouncedQuery(query)
    }, debounceMs)

    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current)
      }
    }
  }, [query, debounceMs])

  // Query con debounce
  const searchQuery = useQuery(
    `search-${debouncedQuery}`,
    () => searchFunction(debouncedQuery),
    {
      enabled: debouncedQuery.length >= 2,
      showToasts: false,
      staleTime: 2 * 60 * 1000 // 2 minutos
    }
  )

  return {
    query,
    setQuery,
    results: searchQuery.data || [],
    loading: searchQuery.loading,
    error: searchQuery.error
  }
}

/**
 * Hook para operaciones optimistas
 */
export function useOptimisticMutation<TData, TVariables>(
  mutationFunction: (variables: TVariables) => Promise<TData>,
  optimisticUpdate: (variables: TVariables, currentData: TData | null) => TData,
  options: UseMutationOptions<TData, TVariables> = {}
) {
  const [optimisticData, setOptimisticData] = useState<TData | null>(null)
  
  const mutation = useMutation(mutationFunction, {
    ...options,
    onSuccess: (data, variables) => {
      setOptimisticData(null) // Limpiar dato optimista
      options.onSuccess?.(data, variables)
    },
    onError: (error, variables) => {
      setOptimisticData(null) // Revertir en caso de error
      options.onError?.(error, variables)
    }
  })

  const mutateOptimistic = useCallback((variables: TVariables) => {
    // Aplicar update optimista
    const newOptimisticData = optimisticUpdate(variables, mutation.data)
    setOptimisticData(newOptimisticData)
    
    // Ejecutar mutación real
    return mutation.mutate(variables)
  }, [mutation, optimisticUpdate])

  return {
    ...mutation,
    data: optimisticData || mutation.data,
    mutate: mutateOptimistic
  }
}

// =============================================================================
// HOOK PARA POLLING
// =============================================================================

/**
 * Hook para polling automático
 */
export function usePolling<TData>(
  queryFunction: () => Promise<TData>,
  interval: number,
  options: { enabled?: boolean; immediate?: boolean } = {}
) {
  const { enabled = true, immediate = true } = options
  
  const query = useQuery(
    `polling-${Date.now()}`,
    queryFunction,
    {
      immediate,
      enabled,
      refetchInterval: enabled ? interval : undefined,
      showToasts: false
    }
  )

  const startPolling = useCallback(() => {
    query.refetch()
  }, [query])

  const stopPolling = useCallback(() => {
    // El polling se detiene automáticamente cuando enabled es false
  }, [])

  return {
    ...query,
    startPolling,
    stopPolling
  }
}

// =============================================================================
// EXPORTACIONES
// =============================================================================

export default useApi