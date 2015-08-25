$(function(){
  var hints = ['IBM中国研究院什么时候成立的？',
               '请告诉我谁是IBM中国研究院的现任院长？',
               '我想知道IBM全球有多少员工？',
               '颐和园的门票多少钱？',
               '大雁塔位于哪里？',
               '苹果公司的员工数量是多少？',
               '英国的首都是什么？',
               '中华人民共和国的国土面积是多少？',
               '哈佛大学的现任校长是谁？',
               '周杰伦的妻子是谁？',
               'Macbook的操作系统是什么？',
               'Windows的最新版本？',
               'Quora的创始人是谁？',
               '太阳的表面温度有多高？',
               '火星的半径有多大？',
               '红高粱的导演是谁？',
               '百度的董事长是？'];

  $('.help-box').mousedown(function(e){
    var that = $(this);
    that.data('dragging', true);
    that.data('ix', e.clientX-this.offsetLeft);
    that.data('iy', e.clientY-this.offsetTop);
  }).mousemove(function(e){
    var that = $(this);
    if(!that.data('dragging'))
      return;
    var oX = e.clientX - that.data('ix');
    var oY = e.clientY - that.data('iy');
    that.css({"left":oX + "px", "top":oY + "px"});
  }).mouseup(function(e){
    var that = $(this);
    that.data('dragging', false);
  });

  $('.help-box .row button').on('countdown', function(e, fn, timeout){
    var that = $(this);
    if(that.data('countdown'))
      return;
    that.data('countdown', timeout || 5);

    var btn_text = that.text();

    function _doCountDown(){
      var time = that.data('countdown');
      if(time == 0){
        that.text(btn_text);
        fn();
      }else{
        time -= 1;
        that.data('countdown', time);
        that.text(btn_text+' ('+time+')');
        setTimeout(_doCountDown, 1000);
      }
    }
    _doCountDown();
  }).on('click', function(){
    var selection = $('.help-box .row select');
    var option = selection.val();
    $('#question').trigger('typeeffect', [hints[option]]);
    if(option != hints.length-1){
      selection.val(parseInt(option, 10)+1);
    }
  });

  $('.help-box').on('demobegin', function(){
    var that = $(this);
    if(that.data('demobegin'))
      return;

    that.data('demobegin', true);
    that.show();/*
    $('.help-box .row button').trigger('countdown', [function(){
      var that = $(this);
      var selection = $('.help-box .row select');
      var option = selection.val();

      $('#question').trigger('typedemo', [hints[option], function(){

      }]);

      alert(option);
    }]);*/
  });

  $('#demo-qa').click(function(){
    $('.help-box').trigger('demobegin');
  });

  (function(){
    var selects = $('.help-box .row select');
    hints.forEach(function(q, i){
      selects.append('<option value="'+i+'">'+q+'</option>');
    });
  })();

  $('#question').on('keydown', function(e){
    if(e.keyCode==13){
      $('#ask').trigger('click');
    }
  }).on('typeeffect', function(e, content, fn){
    var that = $(this);
    that.val('');
    var pos = 0;

    function doType(){
      that.val(that.val() + content[pos++]);
      if(pos >= content.length){
        setTimeout(function(){
          var e = $.Event("keydown");
          e.keyCode = 13;
          that.trigger(e);
          if(fn)
            setTimeout(fn, 500);
        }, 500);
      }
      else
        setTimeout(doType, 70);
    }
    setTimeout(doType, 500);
  });
  $('#ask').on('click', function(){
    $(this).children('span')
      .removeClass('glyphicon-search')
      .addClass('glyphicon-refresh glyphicon-refresh-animate');

    var text = $('#question').val();
    $('#result').hide();

    $.ajax({
      type: 'post',
      data: {
        text: text
      },
      url: 'query/',
      dataType: 'json',
      success: function(d){
        $('#ask').children('span')
          .removeClass('glyphicon-refresh glyphicon-refresh-animate')
          .addClass('glyphicon-search');

        function link_to_ne(result){
          if(result.is_alias){
            return result.ne_display+'，又名<a href="/bdbk/showTuplesForNamedEntity/'+result.ne_id+'/'+'">'+result.ne_title+'</a>';
          }else{
            if(result.ne_display!=result.ne_title)
              return '<a href="/bdbk/showTuplesForNamedEntity/'+result.ne_id+'/'+'">'+result.ne_title + '</a>';
            else
              return '<a href="/bdbk/showTuplesForNamedEntity/'+result.ne_id+'/'+'">'+result.ne_title + '</a>';
          }
        }
        $('#result-words').text(d.tokenize.join(','));

        if(d.result.length){
          $('#best-result-row').show();
          $('#no-result').hide();
          $('#best-result-title').html(link_to_ne(d.result[0])+'的'+d.result[0].verb);
          $('#best-result-content').html(d.result[0].content);
        }
        else{
          $('#best-result-row').hide();
          $('#no-result').show();
        }

        var others = '';
        for(var i=1;i<d.result.length;++i){
          others += '<li>'+link_to_ne(d.result[i]) + '的' + d.result[i].verb + '：' + d.result[i].content+'</li>';
        }
        $('#other-results').html(others);
        if(others.length!=0)
          $('#other-results-row').show();
        else
          $('#other-results-row').hide();

        var nes = '';
        for(var i=0;i<d.named_entities.length;++i){
          nes += '<li>' + link_to_ne(d.named_entities[i])+'</li>';
          //break;
        }
        $('#named-entities').html(nes);
        if(nes.length!=0)
          $('#named-entities-row').show();
        else
          $('#named-entities-row').hide();

        $('#result').show();
      }
    });
  });
});
