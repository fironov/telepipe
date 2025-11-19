import Link from 'next/link';

export default function VideoPage({ video }) {
  if (!video) {
    return (
      <main style={{ maxWidth: 720, margin: '0 auto', padding: '2rem' }}>
        <p>Видео не найдено.</p>
        <Link href="/">Вернуться к списку</Link>
      </main>
    );
  }

  return (
    <main style={{ maxWidth: 720, margin: '0 auto', padding: '2rem' }}>
      <Link href="/">← Назад</Link>
      <h1>{video.title}</h1>
      <p style={{ color: '#666' }}>{video.original_name}</p>
      <video
        key={video.file_url}
        src={video.file_url}
        controls
        style={{ width: '100%', marginTop: '1rem', borderRadius: 8 }}
      />
    </main>
  );
}

export async function getServerSideProps({ params }) {
  const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL ?? 'http://localhost:8000';
  try {
    const response = await fetch(`${apiBase}/videos`);
    if (!response.ok) {
      return { props: { video: null } };
    }
    const videos = await response.json();
    const video = videos.find((item) => String(item.id) === params.id) || null;
    return { props: { video } };
  } catch (error) {
    console.error('Failed to load video', error);
    return { props: { video: null } };
  }
}
