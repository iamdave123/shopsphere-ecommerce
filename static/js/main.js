// Quantity steppers (+ / −) on product & cart pages
document.querySelectorAll("[data-step]").forEach((btn) => {
  btn.addEventListener("click", () => {
    const input = btn.closest(".qty-group").querySelector("input[name=quantity]");
    const step = parseInt(btn.dataset.step, 10);
    const max = parseInt(input.max || "9999", 10);
    let val = parseInt(input.value || "1", 10) + step;
    input.value = Math.min(Math.max(val, 1), max);
    // Auto-submit cart row updates
    const form = btn.closest("form[data-autosubmit]");
    if (form) form.submit();
  });
});

// Dismiss alerts automatically after a few seconds
setTimeout(() => {
  document.querySelectorAll(".alert").forEach((el) => {
    const alert = bootstrap.Alert.getOrCreateInstance(el);
    alert.close();
  });
}, 4500);
