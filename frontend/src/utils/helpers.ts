/**
 * VALIDACIONES PERÚ - PROYECTO FELICITA
 * Sistema de Facturación Electrónica para Perú
 * 
 * Validaciones específicas para documentos y normativas peruanas
 */

// =============================================================================
// TIPOS DE VALIDACIÓN
// =============================================================================

export interface ResultadoValidacion {
  valido: boolean
  mensaje?: string
  datos?: any
}

export type TipoDocumento = 'DNI' | 'RUC' | 'CARNET_EXTRANJERIA' | 'PASAPORTE'

// =============================================================================
// VALIDACIÓN RUC (PERÚ)
// =============================================================================

/**
 * Valida RUC peruano con algoritmo verificador oficial
 */
export const validarRuc = (ruc: string): ResultadoValidacion => {
  // Limpiar RUC
  const rucLimpio = ruc.replace(/\D/g, '')
  
  // Validar longitud
  if (rucLimpio.length !== 11) {
    return {
      valido: false,
      mensaje: 'El RUC debe tener 11 dígitos'
    }
  }
  
  // Validar que no sean todos iguales
  if (/^(\d)\1{10}$/.test(rucLimpio)) {
    return {
      valido: false,
      mensaje: 'El RUC no puede tener todos los dígitos iguales'
    }
  }
  
  // Validar primer dígito según tipo de contribuyente
  const primerDigito = rucLimpio.charAt(0)
  const segundoDigito = rucLimpio.charAt(1)
  
  let tipoContribuyente = ''
  let factores: number[] = []
  
  if (primerDigito === '1' && segundoDigito === '0') {
    // DNI con 10 al inicio (persona natural)
    tipoContribuyente = 'Persona Natural'
    factores = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2]
  } else if (primerDigito === '2' && ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'].includes(segundoDigito)) {
    // Empresa
    tipoContribuyente = 'Empresa'
    factores = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2]
  } else if (primerDigito === '1' && segundoDigito === '5') {
    // Gobierno central
    tipoContribuyente = 'Gobierno Central'
    factores = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2]
  } else if (primerDigito === '1' && segundoDigito === '6') {
    // Gobierno regional
    tipoContribuyente = 'Gobierno Regional'
    factores = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2]
  } else if (primerDigito === '1' && segundoDigito === '7') {
    // Gobierno local
    tipoContribuyente = 'Gobierno Local'
    factores = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2]
  } else {
    return {
      valido: false,
      mensaje: 'Tipo de RUC no válido'
    }
  }
  
  // Calcular dígito verificador
  let suma = 0
  for (let i = 0; i < 10; i++) {
    suma += parseInt(rucLimpio.charAt(i)) * factores[i]
  }
  
  const resto = suma % 11
  const digitoVerificador = resto < 2 ? resto : 11 - resto
  const digitoRuc = parseInt(rucLimpio.charAt(10))
  
  if (digitoVerificador !== digitoRuc) {
    return {
      valido: false,
      mensaje: 'El RUC no es válido (dígito verificador incorrecto)'
    }
  }
  
  return {
    valido: true,
    mensaje: 'RUC válido',
    datos: {
      ruc: rucLimpio,
      tipoContribuyente,
      digitoVerificador
    }
  }
}

/**
 * Formatea RUC con guiones
 */
export const formatearRuc = (ruc: string): string => {
  const rucLimpio = ruc.replace(/\D/g, '')
  if (rucLimpio.length === 11) {
    return `${rucLimpio.substring(0, 2)}-${rucLimpio.substring(2, 10)}-${rucLimpio.substring(10)}`
  }
  return ruc
}

// =============================================================================
// VALIDACIÓN DNI (PERÚ)
// =============================================================================

/**
 * Valida DNI peruano
 */
export const validarDni = (dni: string): ResultadoValidacion => {
  // Limpiar DNI
  const dniLimpio = dni.replace(/\D/g, '')
  
  // Validar longitud
  if (dniLimpio.length !== 8) {
    return {
      valido: false,
      mensaje: 'El DNI debe tener 8 dígitos'
    }
  }
  
  // Validar que no sean todos iguales
  if (/^(\d)\1{7}$/.test(dniLimpio)) {
    return {
      valido: false,
      mensaje: 'El DNI no puede tener todos los dígitos iguales'
    }
  }
  
  // Validar que no sea secuencial
  let esSecuencial = true
  for (let i = 1; i < dniLimpio.length; i++) {
    if (parseInt(dniLimpio[i]) !== parseInt(dniLimpio[i-1]) + 1) {
      esSecuencial = false
      break
    }
  }
  
  if (esSecuencial) {
    return {
      valido: false,
      mensaje: 'El DNI no puede ser secuencial'
    }
  }
  
  // Validar rango básico (DNIs peruanos actuales)
  const dniNumero = parseInt(dniLimpio)
  if (dniNumero < 1000000 || dniNumero > 99999999) {
    return {
      valido: false,
      mensaje: 'DNI fuera del rango válido'
    }
  }
  
  return {
    valido: true,
    mensaje: 'DNI válido',
    datos: {
      dni: dniLimpio
    }
  }
}

/**
 * Formatea DNI con separadores
 */
export const formatearDni = (dni: string): string => {
  const dniLimpio = dni.replace(/\D/g, '')
  if (dniLimpio.length === 8) {
    return `${dniLimpio.substring(0, 2)}.${dniLimpio.substring(2, 5)}.${dniLimpio.substring(5)}`
  }
  return dni
}

// =============================================================================
// VALIDACIÓN CARNET DE EXTRANJERÍA
// =============================================================================

/**
 * Valida Carnet de Extranjería peruano
 */
export const validarCarnetExtranjeria = (carnet: string): ResultadoValidacion => {
  // Limpiar carnet
  const carnetLimpio = carnet.replace(/\D/g, '')
  
  // Validar longitud (9 dígitos)
  if (carnetLimpio.length !== 9) {
    return {
      valido: false,
      mensaje: 'El Carnet de Extranjería debe tener 9 dígitos'
    }
  }
  
  // Validar que no sean todos iguales
  if (/^(\d)\1{8}$/.test(carnetLimpio)) {
    return {
      valido: false,
      mensaje: 'El Carnet no puede tener todos los dígitos iguales'
    }
  }
  
  return {
    valido: true,
    mensaje: 'Carnet de Extranjería válido',
    datos: {
      carnet: carnetLimpio
    }
  }
}

// =============================================================================
// VALIDACIÓN PASAPORTE
// =============================================================================

/**
 * Valida formato básico de pasaporte
 */
export const validarPasaporte = (pasaporte: string): ResultadoValidacion => {
  // Limpiar pasaporte
  const pasaporteLimpio = pasaporte.trim().toUpperCase()
  
  // Validar longitud (6-9 caracteres alfanuméricos)
  if (pasaporteLimpio.length < 6 || pasaporteLimpio.length > 9) {
    return {
      valido: false,
      mensaje: 'El pasaporte debe tener entre 6 y 9 caracteres'
    }
  }
  
  // Validar formato alfanumérico
  if (!/^[A-Z0-9]+$/.test(pasaporteLimpio)) {
    return {
      valido: false,
      mensaje: 'El pasaporte solo puede contener letras y números'
    }
  }
  
  return {
    valido: true,
    mensaje: 'Pasaporte válido',
    datos: {
      pasaporte: pasaporteLimpio
    }
  }
}

// =============================================================================
// VALIDACIÓN UNIVERSAL DE DOCUMENTOS
// =============================================================================

/**
 * Valida documento según su tipo
 */
export const validarDocumento = (
  documento: string, 
  tipo: TipoDocumento
): ResultadoValidacion => {
  switch (tipo) {
    case 'DNI':
      return validarDni(documento)
    case 'RUC':
      return validarRuc(documento)
    case 'CARNET_EXTRANJERIA':
      return validarCarnetExtranjeria(documento)
    case 'PASAPORTE':
      return validarPasaporte(documento)
    default:
      return {
        valido: false,
        mensaje: 'Tipo de documento no reconocido'
      }
  }
}

/**
 * Detecta automáticamente el tipo de documento
 */
export const detectarTipoDocumento = (documento: string): TipoDocumento | null => {
  const docLimpio = documento.replace(/\D/g, '')
  
  if (docLimpio.length === 8) {
    return 'DNI'
  } else if (docLimpio.length === 11) {
    return 'RUC'
  } else if (docLimpio.length === 9) {
    return 'CARNET_EXTRANJERIA'
  } else if (documento.length >= 6 && documento.length <= 9 && /[A-Za-z]/.test(documento)) {
    return 'PASAPORTE'
  }
  
  return null
}

// =============================================================================
// VALIDACIONES DE FACTURACIÓN
// =============================================================================

/**
 * Valida serie de comprobante peruano
 */
export const validarSerieComprobante = (serie: string): ResultadoValidacion => {
  // Limpiar serie
  const serieLimpia = serie.trim().toUpperCase()
  
  // Validar formato: 1 letra + 3 números (ej: F001, B001)
  if (!/^[A-Z]\d{3}$/.test(serieLimpia)) {
    return {
      valido: false,
      mensaje: 'La serie debe tener formato de 1 letra seguida de 3 números (ej: F001)'
    }
  }
  
  // Validar letra inicial según tipo de comprobante
  const letraInicial = serieLimpia.charAt(0)
  const letrasValidas = ['F', 'B', 'E', 'T'] // Factura, Boleta, Exportación, Ticket
  
  if (!letrasValidas.includes(letraInicial)) {
    return {
      valido: false,
      mensaje: 'La serie debe comenzar con F (Factura), B (Boleta), E (Exportación) o T (Ticket)'
    }
  }
  
  return {
    valido: true,
    mensaje: 'Serie válida',
    datos: {
      serie: serieLimpia,
      tipoComprobante: letraInicial === 'F' ? 'Factura' : 
                      letraInicial === 'B' ? 'Boleta' : 
                      letraInicial === 'E' ? 'Exportación' : 'Ticket'
    }
  }
}

/**
 * Valida número de comprobante
 */
export const validarNumeroComprobante = (numero: string | number): ResultadoValidacion => {
  const numeroLimpio = typeof numero === 'string' ? 
    numero.replace(/\D/g, '') : 
    numero.toString()
  
  // Validar que sea numérico
  if (!/^\d+$/.test(numeroLimpio)) {
    return {
      valido: false,
      mensaje: 'El número de comprobante debe ser numérico'
    }
  }
  
  // Validar longitud (máximo 8 dígitos según SUNAT)
  if (numeroLimpio.length > 8) {
    return {
      valido: false,
      mensaje: 'El número de comprobante no puede tener más de 8 dígitos'
    }
  }
  
  // Validar que no sea 0
  if (parseInt(numeroLimpio) === 0) {
    return {
      valido: false,
      mensaje: 'El número de comprobante debe ser mayor a 0'
    }
  }
  
  return {
    valido: true,
    mensaje: 'Número de comprobante válido',
    datos: {
      numero: numeroLimpio.padStart(8, '0') // Formatear con ceros a la izquierda
    }
  }
}

// =============================================================================
// VALIDACIONES DE MONTOS
// =============================================================================

/**
 * Valida monto monetario
 */
export const validarMonto = (monto: number | string): ResultadoValidacion => {
  const montoNumero = typeof monto === 'string' ? parseFloat(monto) : monto
  
  // Validar que sea un número
  if (isNaN(montoNumero)) {
    return {
      valido: false,
      mensaje: 'El monto debe ser un número válido'
    }
  }
  
  // Validar que sea positivo
  if (montoNumero < 0) {
    return {
      valido: false,
      mensaje: 'El monto debe ser positivo'
    }
  }
  
  // Validar que no exceda límites razonables
  if (montoNumero > 999999999.99) {
    return {
      valido: false,
      mensaje: 'El monto excede el límite máximo'
    }
  }
  
  // Validar máximo 2 decimales
  const decimales = montoNumero.toString().split('.')[1]
  if (decimales && decimales.length > 2) {
    return {
      valido: false,
      mensaje: 'El monto no puede tener más de 2 decimales'
    }
  }
  
  return {
    valido: true,
    mensaje: 'Monto válido',
    datos: {
      monto: Math.round(montoNumero * 100) / 100 // Redondear a 2 decimales
    }
  }
}

// =============================================================================
// VALIDACIONES DE EMAIL Y TELÉFONO
// =============================================================================

/**
 * Valida email con formato peruano
 */
export const validarEmail = (email: string): ResultadoValidacion => {
  const emailLimpio = email.trim().toLowerCase()
  
  // Validar formato básico
  const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!regex.test(emailLimpio)) {
    return {
      valido: false,
      mensaje: 'Formato de email inválido'
    }
  }
  
  // Validar longitud
  if (emailLimpio.length > 254) {
    return {
      valido: false,
      mensaje: 'Email demasiado largo'
    }
  }
  
  return {
    valido: true,
    mensaje: 'Email válido',
    datos: {
      email: emailLimpio
    }
  }
}

/**
 * Valida teléfono peruano
 */
export const validarTelefono = (telefono: string): ResultadoValidacion => {
  // Limpiar teléfono
  const telefonoLimpio = telefono.replace(/\D/g, '')
  
  // Validar longitud (móvil: 9 dígitos, fijo: 7 dígitos con código de área)
  if (telefonoLimpio.length === 9) {
    // Móvil: debe empezar con 9
    if (!telefonoLimpio.startsWith('9')) {
      return {
        valido: false,
        mensaje: 'Los teléfonos móviles deben empezar con 9'
      }
    }
  } else if (telefonoLimpio.length === 7) {
    // Teléfono fijo sin código de área
  } else if (telefonoLimpio.length >= 9 && telefonoLimpio.length <= 11) {
    // Teléfono con código de área
  } else {
    return {
      valido: false,
      mensaje: 'Número de teléfono inválido'
    }
  }
  
  return {
    valido: true,
    mensaje: 'Teléfono válido',
    datos: {
      telefono: telefonoLimpio
    }
  }
}

// =============================================================================
// UTILITARIO GENERAL DE VALIDACIÓN
// =============================================================================

/**
 * Valida múltiples campos a la vez
 */
export const validarCampos = (
  campos: Record<string, { valor: any; validador: (valor: any) => ResultadoValidacion }>
): { valido: boolean; errores: Record<string, string> } => {
  const errores: Record<string, string> = {}
  let todosValidos = true
  
  Object.entries(campos).forEach(([campo, { valor, validador }]) => {
    const resultado = validador(valor)
    if (!resultado.valido) {
      errores[campo] = resultado.mensaje || 'Campo inválido'
      todosValidos = false
    }
  })
  
  return {
    valido: todosValidos,
    errores
  }
}