module.exports = {
  env: {
    browser: true,
    commonjs: true,
    es2021: true,
  },
  extends: "standard-with-typescript",
  parserOptions: {
    ecmaVersion: "latest",
  },
  rules: {
    camelcase: "error",
    "spaced-comment": "error",
    quotes: ["error", "single"],
    "no-duplicate-imports": "error",
    semi: ["error", "always"],
  },
};
