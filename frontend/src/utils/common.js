export function setObj(key, obj) {
  obj = JSON.stringify(obj);
  localStorage.setItem(key, obj);
}

export function getObj(key) {
  let obj = JSON.parse(localStorage.getItem(key));
  return obj;
}
