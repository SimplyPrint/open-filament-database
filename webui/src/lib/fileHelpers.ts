import fs from "node:fs";

export function getFiles(path: string): string[]|null {
    if (fs.existsSync(path)) {
        let files: string[] = [];

        fs.readdirSync(path).forEach(file => {
                files.push(`${path}/${file}`);
        });

        return files;
    }

    return null;
}

export function getFolders(path: string): string[]|null {
    let files = getFiles(path);
    if (!files) {
        return null;
    }

    files = files.filter((file) => fs.lstatSync(file).isDirectory());

    return files;
}

export function loadFilesInDir<T>(path: string, filePath: string): T[]|null {
    let paths = getFolders(path);
    let vars: T[] = [];

    paths?.forEach((path) => {
        let fileData = readFile(`${path}/${filePath}`);
        if (!fileData) {
            return;
        }

        let parsed = JSON.parse(fileData);

        vars.push(parsed);
    });

    return vars;
}

export function readFile(path: string): string|null {
    let data = fs.readFileSync(path, "utf8");
    
    return data;
}