import Link from 'next/link';

export default function Home({ videos }) {
  return (
    <main style={{ maxWidth: 720, margin: '0 auto', padding: '2rem' }}>
      <h1>Моя видеотека</h1>
      {videos.length === 0 ? (
        <p>Загрузите видео через Telegram-бота.</p>
      ) : (
        <ul style={{ listStyle: 'none', padding: 0 }}>
          {videos.map((video) => (
            <li
              key={video.id}
              style={{
                border: '1px solid #ddd',
                borderRadius: 8,
                padding: '1rem',
                marginBottom: '1rem',
              }}
            >
              <h3 style={{ margin: '0 0 0.5rem' }}>{video.title}</h3>
              <p style={{ margin: '0 0 0.5rem', color: '#666' }}>
                {video.original_name} • {(video.size / (1024 * 1024)).toFixed(2)} MB
              </p>
              <Link href={`/video/${video.id}`}>Смотреть</Link>
            </li>
          ))}
        </ul>
      )}
    </main>
  );
}

export async function getServerSideProps() {
  const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL ?? 'http://localhost:8000';
  try {
    const response = await fetch(`${apiBase}/videos`);
    const videos = response.ok ? await response.json() : [];
    return { props: { videos } };
  } catch (error) {
    console.error('Failed to load videos', error);
    return { props: { videos: [] } };
  }
}
