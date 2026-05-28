import { getCollection } from "astro:content";

export async function getPageStaticPaths() {
  const pages = await getCollection("pages");

  return pages.map(page => ({
    params: { slug: page.id },
    props: { page },
  }));
}
