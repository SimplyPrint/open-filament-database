import { object } from "zod";

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