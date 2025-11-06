db.catalogo_livros.createIndex({ 
  titulo: "text", 
  autor: "text", 
  tags: "text" 
})

db.catalogo_livros.find({
  $text: { $search: "machado assis romance" },
  disponivel: true
}).sort({ nota_media: -1 })