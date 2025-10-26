import { env } from "$env/dynamic/public";
import { loadFilesInDir } from "$lib/fileHelpers.js";
import { json } from "@sveltejs/kit";
import type { RequestEvent } from "./$types";
import type { Filament } from "$lib/validation";

export async function GET(event: RequestEvent) {
    let filaments = loadFilesInDir<Filament>(
        `${env.PUBLIC_DATA_PATH}/${event.params.brand}/${event.params.material}`,
        "filament.json"
    );

    return json({
        filaments: filaments
    });
}