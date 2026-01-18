use counter_applet::CounterApplet;

#[test]
fn test_counter_full_workflow() {
    let mut counter = CounterApplet::new("alice".to_string());
    
    // Initial state
    assert_eq!(counter.get_count(), 0);
    assert_eq!(counter.get_owner(), "alice");
    
    // Basic operations
    assert_eq!(counter.increment(), 1);
    assert_eq!(counter.increment(), 2);
    assert_eq!(counter.add(3), 5);
    assert_eq!(counter.decrement(), 4);
    
    // Set specific value
    assert_eq!(counter.set_count(42), 42);
    assert_eq!(counter.get_count(), 42);
    
    // Reset
    assert_eq!(counter.reset(), 0);
    assert_eq!(counter.get_count(), 0);
    
    // State serialization
    let state_json = counter.get_state();
    assert!(state_json.contains("\"count\":0"));
    assert!(state_json.contains("\"owner\":\"alice\""));
}

#[test]
fn test_counter_negative_values() {
    let mut counter = CounterApplet::new("bob".to_string());
    
    // Test negative operations
    assert_eq!(counter.decrement(), -1);
    assert_eq!(counter.add(-5), -6);
    assert_eq!(counter.set_count(-10), -10);
    
    // Back to positive
    assert_eq!(counter.add(15), 5);
}