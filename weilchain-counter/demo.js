// Simple demo of the Counter Applet functionality
// This simulates how the applet would work on Weilchain

class CounterApplet {
  constructor(owner) {
    this.state = {
      count: 0,
      owner: owner
    };
  }

  getCount() {
    return this.state.count;
  }

  increment() {
    this.state.count += 1;
    return this.state.count;
  }

  decrement() {
    this.state.count -= 1;
    return this.state.count;
  }

  add(value) {
    this.state.count += value;
    return this.state.count;
  }

  setCount(value) {
    this.state.count = value;
    return this.state.count;
  }

  reset() {
    this.state.count = 0;
    return this.state.count;
  }

  getOwner() {
    return this.state.owner;
  }

  getState() {
    return JSON.stringify(this.state);
  }
}

// Demo execution
console.log("🚀 Weilchain Counter Applet Demo");
console.log("================================");

const counter = new CounterApplet("alice");

console.log(`📊 Initial count: ${counter.getCount()}`);
console.log(`👤 Owner: ${counter.getOwner()}`);

console.log(`⬆️  Increment: ${counter.increment()}`);
console.log(`⬆️  Increment: ${counter.increment()}`);
console.log(`➕ Add 5: ${counter.add(5)}`);
console.log(`⬇️  Decrement: ${counter.decrement()}`);
console.log(`🔢 Set to 100: ${counter.setCount(100)}`);
console.log(`🔄 Reset: ${counter.reset()}`);

console.log(`📋 Final state: ${counter.getState()}`);

console.log("\n✅ Demo completed successfully!");
console.log("\nNext steps:");
console.log("1. Install Weilchain CLI");
console.log("2. Deploy this applet to a Weilchain network");
console.log("3. Interact via CLI, Block Explorer, or MCP Server");