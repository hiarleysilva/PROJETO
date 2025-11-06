db.avaliacoes_livros.aggregate([
  {
    $group: {
      _id: "$livro_id",
      media_avaliacao: { $avg: "$nota" },
      total_avaliacoes: { $sum: 1 },
      ultima_avaliacao: { $max: "$data_avaliacao" }
    }
  },
  { $match: { total_avaliacoes: { $gte: 10 } } },
  { $sort: { media_avaliacao: -1, total_avaliacoes: -1 } },
  { $limit: 10 }
])