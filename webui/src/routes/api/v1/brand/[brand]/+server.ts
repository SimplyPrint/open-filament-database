import { env } from "$env/dynamic/public";
import { loadFilesInDir } from "$lib/fileHelpers.js";
import { json } from "@sveltejs/kit";
import type { RequestEvent } from "./$types";
import type { Material } from "$lib/validation";

export async function GET(event: RequestEvent) {
    let materials = loadFilesInDir<Material>(
        `${env.PUBLIC_DATA_PATH}/${event.params.brand}`,
        'material.json'
    );
    
    return json({
        materials: materials
    });
}