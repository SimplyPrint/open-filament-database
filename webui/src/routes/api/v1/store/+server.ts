import { env } from "$env/dynamic/public";
import type { Store } from "$lib/validation.js";
import { json } from "@sveltejs/kit";
import type { RequestEvent } from "./$types";
import { loadFilesInDir } from "$lib/fileHelpers.js";

export async function GET(event: RequestEvent) {
    let stores = loadFilesInDir<Store>(
        env.PUBLIC_STORES_PATH,
        'store.json'
    );
    
    return json({
        stores: stores
    });
}