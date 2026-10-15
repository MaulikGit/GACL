import { defineConfig } from "astro/config";

export default defineConfig({
  site: "https://www.gacl.com",
  trailingSlash: "always",
  build: { format: "directory" },
});
