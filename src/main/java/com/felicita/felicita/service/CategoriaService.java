package com.felicita.felicita.service;

import com.felicita.felicita.dto.MensajeResponse;
import com.felicita.felicita.model.Categoria;
import com.felicita.felicita.repository.CategoriaRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.List;
import java.util.Optional;

/**
 * Servicio que gestiona las operaciones relacionadas con las categorías de servicios.
 */
@Service
public class CategoriaService {

    @Autowired
    private CategoriaRepository categoriaRepository;
    
    /**
     * Obtiene todas las categorías
     * @return Lista de categorías
     */
    public List<Categoria> obtenerTodas() {
        return categoriaRepository.findAll();
    }
    
    /**
     * Obtiene todas las categorías activas
     * @return Lista de categorías activas
     */
    public List<Categoria> obtenerTodasActivas() {
        try {
            return categoriaRepository.findByActivoTrue();
        } catch (Exception e) {
            System.err.println("Error en obtenerTodasActivas: " + e.toString());
            e.printStackTrace();
            return new ArrayList<>();
        }
    }
    
    /**
     * Obtiene todas las categorías activas ordenadas
     * @return Lista de categorías activas ordenadas
     */
    public List<Categoria> obtenerTodasActivasOrdenadas() {
        try {
            return categoriaRepository.findByActivoTrueOrderByOrdenAsc();
        } catch (Exception e) {
            System.err.println("Error en obtenerTodasActivasOrdenadas: " + e.toString());
            e.printStackTrace();
            return obtenerTodasActivas(); // Fallback a categorías sin ordenar
        }
    }
    
    /**
     * Busca una categoría por su ID
     * @param id ID de la categoría
     * @return Categoría si existe, vacío si no
     */
    public Optional<Categoria> obtenerPorId(Long id) {
        return categoriaRepository.findById(id);
    }
    
    /**
     * Busca una categoría por su nombre
     * @param nombre Nombre de la categoría
     * @return Categoría si existe, vacío si no
     */
    public Optional<Categoria> obtenerPorNombre(String nombre) {
        return categoriaRepository.findByNombre(nombre);
    }
    
    /**
     * Busca categorías que contengan el texto proporcionado en su nombre
     * @param nombre Texto a buscar
     * @return Lista de categorías que coinciden
     */
    public List<Categoria> buscarPorNombre(String nombre) {
        return categoriaRepository.findByNombreContainingAndActivoTrue(nombre);
    }
    
    /**
     * Crea una nueva categoría
     * @param categoria Datos de la categoría a crear
     * @return Categoría creada
     */
    public Categoria crearCategoria(Categoria categoria) {
        return categoriaRepository.save(categoria);
    }
    
    /**
     * Actualiza una categoría existente
     * @param id ID de la categoría a actualizar
     * @param categoriaDetalles Datos actualizados
     * @return Mensaje con el resultado de la operación
     */
    public MensajeResponse actualizarCategoria(Long id, Categoria categoriaDetalles) {
        return categoriaRepository.findById(id)
            .map(categoria -> {
                categoria.setNombre(categoriaDetalles.getNombre());
                categoria.setDescripcion(categoriaDetalles.getDescripcion());
                categoria.setIcono(categoriaDetalles.getIcono());
                categoria.setOrden(categoriaDetalles.getOrden());
                
                categoriaRepository.save(categoria);
                return new MensajeResponse("Categoría actualizada exitosamente", true);
            })
            .orElse(new MensajeResponse("No se encontró la categoría con ID: " + id, false));
    }
    
    /**
     * Cambia el estado de activación de una categoría
     * @param id ID de la categoría
     * @param activo Nuevo estado
     * @return Mensaje con el resultado de la operación
     */
    public MensajeResponse cambiarEstadoActivacion(Long id, boolean activo) {
        return categoriaRepository.findById(id)
            .map(categoria -> {
                categoria.setActivo(activo);
                categoriaRepository.save(categoria);
                String mensaje = activo ? "Categoría activada exitosamente" : "Categoría desactivada exitosamente";
                return new MensajeResponse(mensaje, true);
            })
            .orElse(new MensajeResponse("No se encontró la categoría con ID: " + id, false));
    }
    
    /**
     * Elimina una categoría
     * @param id ID de la categoría a eliminar
     * @return Mensaje con el resultado de la operación
     */
    public MensajeResponse eliminarCategoria(Long id) {
        return categoriaRepository.findById(id)
            .map(categoria -> {
                // Verificar que no tenga servicios asociados
                if (!categoria.getServicios().isEmpty()) {
                    return new MensajeResponse("No se puede eliminar la categoría porque tiene servicios asociados", false);
                }
                
                categoriaRepository.delete(categoria);
                return new MensajeResponse("Categoría eliminada exitosamente", true);
            })
            .orElse(new MensajeResponse("No se encontró la categoría con ID: " + id, false));
    }
    
    /**
     * Obtiene los nombres de todas las categorías activas
     * @return Lista de nombres de categorías
     */
    public List<String> obtenerNombresCategorias() {
        List<Categoria> categorias = obtenerTodasActivasOrdenadas();
        List<String> nombres = new ArrayList<>();
        
        for (Categoria categoria : categorias) {
            nombres.add(categoria.getNombre());
        }
        
        return nombres;
    }
    
    /**
     * Obtiene las categorías predeterminadas si no existen
     * @return Lista de categorías predeterminadas
     */
    public List<Categoria> obtenerCategoriasPrederminadas() {
        List<Categoria> categoriasPredeterminadas = new ArrayList<>();
        
        // Solo crear categorías predeterminadas si no existen
        if (categoriaRepository.count() == 0) {
            String[][] categoriasData = {
                {"Cabello", "Servicios para el cuidado del cabello", "fa-cut", "1"},
                {"Uñas", "Servicios de manicura y pedicura", "fa-hand-sparkles", "2"},
                {"Facial", "Tratamientos faciales y limpieza", "fa-spa", "3"},
                {"Barbería", "Servicios especializados para caballeros", "fa-razor", "4"},
                {"Spa", "Servicios de relajación y bienestar", "fa-hot-tub", "5"}
            };
            
            for (String[] data : categoriasData) {
                Categoria categoria = new Categoria();
                categoria.setNombre(data[0]);
                categoria.setDescripcion(data[1]);
                categoria.setIcono(data[2]);
                categoria.setOrden(Integer.parseInt(data[3]));
                categoria.setActivo(true);
                
                categoriasPredeterminadas.add(categoriaRepository.save(categoria));
            }
        }
        
        return categoriasPredeterminadas;
    }

    

}