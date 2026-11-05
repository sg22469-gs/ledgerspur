export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    // 1. Permanent 301 Redirect for www -> apex (US SEO best practice)
    if (url.hostname.startsWith("www.")) {
      url.hostname = url.hostname.replace(/^www\./, "");
      return Response.redirect(url.toString(), 301);
    }

    // 2. Serve static assets directly from Cloudflare Edge
    return env.ASSETS.fetch(request);
  }
};
