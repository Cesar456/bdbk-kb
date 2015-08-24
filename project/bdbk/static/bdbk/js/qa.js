$(function(){
  $('#question').on('keydown', function(e){
    if(e.keyCode==13){
      $('#ask').trigger('click');
    }
  });
  $('#ask').on('click', function(){
    $(this).children('span')
      .removeClass('glyphicon-search')
      .addClass('glyphicon-refresh glyphicon-refresh-animate');

    var text = $('#question').val();

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
          $('#best-result').html(link_to_ne(d.result[0])+'的'+d.result[0].verb+'：'+d.result[0].content);
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
