(function($){
    jQuery(function(){
      flashembed('video_wrapper', {
          src: 'http://www.youtube.com/v/Xf8VePS4X9I&hl=en&fs=1&ap=%2526fmt%3D18&autoplay=1&rel=0&border=0&loop=0',
          wmode: 'transparent',
          loop: 'false',
          allowFullScreen: 'true',
          allowscriptaccess: 'always',
          height: '280px'
      });
      jQuery("#tweets").tweet({
        username: ['closummitindia'],
        count: 2,
        auto_join_text_default: "we said,",
        auto_join_text_ed: "we",
        auto_join_text_ing: "we were",
        auto_join_text_reply: "we replied to",
        auto_join_text_url: "we were checking out"
    });
      jQuery('#qoutes').innerfade({
          animationtype: 'fade',
          speed: 'slow',
          timeout: 6000,
          type: 'random',
          containerheight: '120px'
      });
      jQuery('#theme').innerfade({
          animationtype: 'slide',
          speed: 'slow',
          timeout: 2000,
          type: 'sequence',
          containerheight: '88px'
      });
      jQuery('.toggle_view a[href="advisory_board"]').toggle(function(){
            jQuery('#advisory_board').css('display', 'none');
        }, function(){
            jQuery('#advisory_board').css('display', 'block');
        });
    });
})(jQuery);
