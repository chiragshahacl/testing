export const formatDOBinput = (value: string) => {
  let formattedValue = '';

  if (value.length > 4) {
    formattedValue = value.slice(0, 4);

    if (value.length > 6) {
      formattedValue += '-' + value.slice(4, 6);

      if (value.length > 8) {
        formattedValue += '-' + value.slice(6, 8);
      } else {
        formattedValue += '-' + value.slice(6);
      }
    } else {
      formattedValue += '-' + value.slice(4);
    }
  } else {
    formattedValue = value;
  }

  return formattedValue;
};
