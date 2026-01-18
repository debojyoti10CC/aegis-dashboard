/**
 * Counter Applet for Weilchain - TypeScript Implementation
 */

interface CounterState {
  count: number;
  owner: string;
}

export class CounterApplet {
  private state: CounterState;

  constructor(owner: string) {
    this.state = {
      count: 0,
      owner: owner
    };
  }

  /**
   * Get the current count
   */
  getCount(): number {
    return this.state.count;
  }

  /**
   * Increment the counter by 1
   */
  increment(): number {
    this.state.count += 1;
    return this.state.count;
  }

  /**
   * Decrement the counter by 1
   */
  decrement(): number {
    this.state.count -= 1;
    return this.state.count;
  }

  /**
   * Add a specific value to the counter
   */
  add(value: number): number {
    this.state.count += value;
    return this.state.count;
  }

  /**
   * Set the counter to a specific value
   */
  setCount(value: number): number {
    this.state.count = value;
    return this.state.count;
  }

  /**
   * Reset the counter to 0
   */
  reset(): number {
    this.state.count = 0;
    return this.state.count;
  }

  /**
   * Get the owner of the counter
   */
  getOwner(): string {
    return this.state.owner;
  }

  /**
   * Get the current state as JSON
   */
  getState(): string {
    return JSON.stringify(this.state);
  }

  /**
   * Serialize state for blockchain storage
   */
  serialize(): Uint8Array {
    const stateJson = JSON.stringify(this.state);
    return new TextEncoder().encode(stateJson);
  }

  /**
   * Deserialize state from blockchain storage
   */
  static deserialize(data: Uint8Array, owner: string): CounterApplet {
    const stateJson = new TextDecoder().decode(data);
    const state = JSON.parse(stateJson) as CounterState;
    
    const applet = new CounterApplet(owner);
    applet.state = state;
    return applet;
  }
}

// Weilchain applet interface functions
// These would be called by the Weilchain runtime

let appletInstance: CounterApplet | null = null;

export function init(owner: string): void {
  appletInstance = new CounterApplet(owner);
}

export function getCount(): number {
  if (!appletInstance) throw new Error("Applet not initialized");
  return appletInstance.getCount();
}

export function increment(): number {
  if (!appletInstance) throw new Error("Applet not initialized");
  return appletInstance.increment();
}

export function decrement(): number {
  if (!appletInstance) throw new Error("Applet not initialized");
  return appletInstance.decrement();
}

export function add(value: number): number {
  if (!appletInstance) throw new Error("Applet not initialized");
  return appletInstance.add(value);
}

export function setCount(value: number): number {
  if (!appletInstance) throw new Error("Applet not initialized");
  return appletInstance.setCount(value);
}

export function reset(): number {
  if (!appletInstance) throw new Error("Applet not initialized");
  return appletInstance.reset();
}

export function getOwner(): string {
  if (!appletInstance) throw new Error("Applet not initialized");
  return appletInstance.getOwner();
}

export function getState(): string {
  if (!appletInstance) throw new Error("Applet not initialized");
  return appletInstance.getState();
}