import { browser } from '$app/environment';

const illegal_characters = [
  "#","%","&","{","}","\\","<",
  ">","*","?","/","$","!","'",
  '"',":","@","+","`","|","="
];
// This should at all times be the same as /data_validator.py:22

export const stripOfIllegalChars = (input: string): string => {
  let value = input;

  illegal_characters.forEach((char) => {
    value = value.replaceAll(char, "");
  })

  return value;
};

export const isEmpty = (obj: Object): boolean => {
  for (var prop in obj) {
    if (Object.prototype.hasOwnProperty.call(obj, prop)) {
      return false;
    }
  }

  Object.values(obj).filter((value) => {
    if (!value) {
      return false;
    }
  });
  
  return true
}

export const isEmptyObject = (value: any): boolean => {
  if (value == null) {
    // null or undefined
    return false;
  }

  if (typeof value !== 'object') {
    // boolean, number, string, function, etc.
    return false;
  }

  const proto = Object.getPrototypeOf(value);

  // consider `Object.create(null)`, commonly used as a safe map
  // before `Map` support, an empty object as well as `{}`
  if (proto !== null && proto !== Object.prototype) {
    return false;
  }

  return isEmpty(value);
}

export const isValidJSON = (jsonString: string): boolean => {
  try {
    JSON.parse(jsonString);
    return true;
  } catch (e) {
    return false;
  }
}

export const capitalizeFirstLetter = (val: string) => {
  return String(val).charAt(0).toUpperCase() + String(val).slice(1);
};

/*
D:/SP/open-filament-database/webui/src/lib/globalHelpers.ts:85
      throw new Error("Unsupported file type in Node.js (must be Buffer or Uint8Array)");
            ^

Error: Unsupported file type in Node.js (must be Buffer or Uint8Array)
    at getImageDimensions (D:/SP/open-filament-database/webui/src/lib/globalHelpers.ts:85:13)

Node.js v24.5.0

export const getImageDimensions = async (file) => {
  if (!browser) {
    // Use 'sharp' in Node.js
    const sharp = await import('sharp');

    let buffer;
    if (Buffer.isBuffer(file)) {
      buffer = file;
    } else if (file instanceof Uint8Array) {
      buffer = Buffer.from(file);
    } else {
      throw new Error('Unsupported file type in Node.js (must be Buffer or Uint8Array)');
    }

    const metadata = await sharp(buffer).metadata();
    return {
      width: metadata.width,
      height: metadata.height,
      format: metadata.format,
    };
  } else {
    // Use <img> in Browser
    return new Promise((resolve, reject) => {
      const blob = file instanceof Blob ? file : new Blob([file]);
      const img = new Image();

      img.onload = () => {
        resolve({ width: img.width, height: img.height });
      };
      img.onerror = reject;

      const url = URL.createObjectURL(blob);
      img.src = url;
    });
  }
}
*/