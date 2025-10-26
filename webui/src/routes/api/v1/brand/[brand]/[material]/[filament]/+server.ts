import { env } from "$env/dynamic/public";
import { loadFilesInDir, readFile } from "$lib/fileHelpers.js";
import { json } from "@sveltejs/kit";
import type { RequestEvent } from "./$types";
import type { FilamentSizeArray, Variant } from "$lib/validation";

export async function GET(event: RequestEvent) {
    let path = `${env.PUBLIC_DATA_PATH}/${event.params.brand}/${event.params.material}/${event.params.filament}`;

    let variants = loadFilesInDir<Variant>(
        path,
        "variant.json"
    );

    variants?.forEach((variant) => {
        let file = readFile(`${path}/${variant.color_name}/sizes.json`);
        if (!file) {
            return;
        }

        let sizes: FilamentSizeArray = JSON.parse(file);
        variant["sizes"] = sizes;
    });

    return json({
        variants: variants
    });
}