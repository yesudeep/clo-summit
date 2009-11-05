jQuery(function() {
  jQuery("#sponsors li a[title]").qtip({
    position: {
      target: 'mouse',
      corner: {
        target: "bottomRight",
        tooltip: "bottomMidlle"
      }
    },
    style: {
      width: 400,
      padding: 5,
      color: 'black',
      textAlign: 'center',
      border: {
        radius: 5
      },
      name: 'cream'
    }
  });
});

