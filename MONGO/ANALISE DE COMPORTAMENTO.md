db.historico_buscas.aggregate([
  {
    $match: {
      timestamp: {
        $gte: ISODate("2024-01-01"),
        $lte: ISODate("2024-01-31")
      }
    }
  },
  {
    $group: {
      _id: "$termo_busca",
      total_buscas: { $sum: 1 },
      usuarios_unicos: { $addToSet: "$usuario_id" },
      taxa_sucesso: { 
        $avg: { 
          $cond: [{ $gt: ["$resultados_encontrados", 0] }, 1, 0] 
        } 
      }
    }
  },
  { $sort: { total_buscas: -1 } }
])