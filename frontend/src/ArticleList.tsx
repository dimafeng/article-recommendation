import React, { useState, useEffect } from 'react';
import relativeTime from 'dayjs/plugin/relativeTime';
import axios from 'axios';
import dayjs from 'dayjs';

interface Candidate {
    content_id: string;
    created: string;
    updated: string;
}

interface Article {
    id: string;
    title: string;
    url: string;
    created: string;
    data: {
        title: string;
        html: string;
        movies: string[];
        top_image: string;
        summary: string;
    }
}

interface ArticleWithCandidate extends Article, Candidate {}

dayjs.extend(relativeTime)

const ArticlesList = () => {
  const [articles, setArticles] = useState<ArticleWithCandidate[]>([]);
  const [selectedArticle, setSelectedArticle] = useState<Article | null>(null);

  useEffect(() => {
    // Fetch articles from endpoint
    const fetchArticles = async () => {
      try {
        const response: Candidate[] = (await axios.get('http://localhost:8000/candidates') as any).data;
        const content_ids: string = response.map((candidate: any) => candidate.content_id).join(',');
        const articles: Article[] = (await axios.get(`http://localhost:8000/contents?content_ids=${content_ids}`)as any).data;
        const articlesWithCandidates = response.map((candidate: Candidate) => {
            const article = articles.find((article) => article.id === candidate.content_id);
            return {
                ...article,
                ...candidate
            } as ArticleWithCandidate
        })
        setArticles(articlesWithCandidates);
      } catch (error) {
        console.error('Error fetching articles:', error);
      }
    };

    fetchArticles();
  }, []);



  console.log(articles);

  return (
    <div className="container">
      {!selectedArticle && (
        <div>
      <h1>Articles List</h1>
      <ul className="articles-list">
        {articles.map((article) => (
          <div key={article.content_id} onClick={() => setSelectedArticle(article)}>
            <h2>{article.title}</h2>
            <p><small>{article.data.summary}</small></p>
          </div>
        ))}
      </ul></div>)}
      {selectedArticle && ([
        <div className="meta">
            <div className="image" style={{backgroundImage: "url(" + selectedArticle.data.top_image + ")"}}></div>
            <div className="info">
                <h1>{selectedArticle.title}</h1>
                <p className='subtitle'>{selectedArticle.data.summary}</p>
                <p className='date'>{dayjs(selectedArticle.created).fromNow() }</p>
                <p><a href={selectedArticle.url}>{selectedArticle.url}</a></p>
            </div>
        </div>,
        <main className='article' dangerouslySetInnerHTML={{__html: selectedArticle.data.html}} />
      ]
      )}
    </div>
  );
};

export default ArticlesList;