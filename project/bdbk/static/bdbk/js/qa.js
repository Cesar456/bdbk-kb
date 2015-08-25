$(function(){
  $('#question').focus(function(){
    $(this).val($('#question-hint').hide().text());
  });
  $('#question').on('keydown', function(e){
    if(e.keyCode==13){
      $('#ask').trigger('click');
    }
  });

  var hints = ['颐和园的门票多少钱？',
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
  function animateHint(){
    var hintContainer = $('#question-hint');
    if(hintContainer.is(':hidden'))
      return;

    var i = Math.floor(Math.random() * hints.length);
    hintContainer.fadeTo(500, 0, function(){
      $(this).text(hints[i]).fadeTo(500, 1, function(){
        setTimeout(animateHint, 2000);
      });
    });
  }
  animateHint();
  $.getJSON('hints/', function(d){
    var r = [];
    for(var i=0;i<d.length;++i){
      hints.push(d[i][0]+'的'+d[i][1]+'是？');
    }
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
