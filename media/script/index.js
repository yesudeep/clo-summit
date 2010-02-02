 jQuery(function(){
 flashembed('video_wrapper', {
     src: 'http://www.youtube.com/cp/vjVQa1PpcFP0swE3qxYKvsq39pbnf9qow-F2s-62UUo=&autoplay=1&rel=0&border=0&loop=0',
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
     type: 'sequence',
     containerheight: '120px'
 });
 jQuery('#theme').innerfade({
     animationtype: 'slide',
     speed: 'slow',
     timeout: 2000,
     type: 'sequence',
     containerheight: '88px'
 });
});
 

