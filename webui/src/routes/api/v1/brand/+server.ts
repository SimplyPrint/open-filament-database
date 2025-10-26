import { env } from "$env/dynamic/public";
import type { Brand } from "$lib/validation.js";
import { json } from "@sveltejs/kit";
import type { RequestEvent } from "./$types";
import { loadFilesInDir } from "$lib/fileHelpers.js";

export async function GET(event: RequestEvent) {
    let brands = loadFilesInDir<Brand>(
        env.PUBLIC_DATA_PATH,
        'brand.json'
    );
    
    return json({
        brands: brands
    });
}