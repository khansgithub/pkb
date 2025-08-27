export function observeObject<T extends object>(obj: T): T {
  return new Proxy(obj, {
    set(target, property, value, receiver) {
      // Trigger debugger when a property is changed
      if (property == "query"){
        console.log(`Property "${String(property)}" changed from`, target[property as keyof T], 'to', value);
        debugger; 
      }
      return Reflect.set(target, property, value, receiver);
    }
  });
}