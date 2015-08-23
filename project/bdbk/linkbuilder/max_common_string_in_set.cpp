#include<cwchar>
#include<string>
#include<iostream>
#include<map>
#include<utility>


class InversedDict{
  wchar_t chr;
  bool isroot;
  std::wstring *value;
  std::map<wchar_t, InversedDict*> submaps;
public:
  InversedDict(){
    this->chr = 0;
    this->isroot = true;
    this->value = NULL;
  }

  InversedDict(wchar_t chr, bool isroot=true){
    this->chr = chr;
    this->isroot = isroot;
    this->value = NULL;
  }

  void set(std::wstring key, std::wstring value){
    if(key.size()==0){
      this->value = new std::wstring(value);
    }else{
      wchar_t chr = key[0];
      auto search = this->submaps.find(chr);
      if(search != this->submaps.end())
        search->second->set(key.substr(1), value);
      else{
        InversedDict* d = new InversedDict(chr, false);
        d->set(key.substr(1), value);
        this->submaps[chr] = d;
      }
    }
  }

  std::wstring* get(std::wstring key){
    if(key.size()==0){
      if(this->isroot)
        return NULL;

      return this->value;
    }else{
      wchar_t chr = key[0];
      auto search = this->submaps.find(chr);
      if(search != this->submaps.end())
        return search->second->get(key.substr(1));
      else
        return NULL;
    }
  }

  void match(std::wstring& key, size_t pos, std::wstring** out_value, size_t* out_end, bool root=true){
    if(root){
      *out_end = pos;
      *out_value = NULL;
    }
    if(pos >= key.size()){
      return;
    } else {
      wchar_t chr = key[pos];
      auto search = this->submaps.find(chr);
      if(search != this->submaps.end()){
        search->second->match(key, pos+1, out_value, out_end, false);
        if(*out_value == NULL){
          *out_value = search->second->value;
          *out_end = pos+1;
        }
      } else {
        return;
      }
    }
  }

};

void handleContinuousMode(InversedDict& dict){
  std::wstring line;
  while(true){
    std::getline(std::wcin, line);
    if(!line.size()){
      std::cerr<<"null string received, exiting."<<std::endl;
      break;
    }

    std::wstring* output_str;
    std::wstring nolink_part;

    for(size_t pos=0;pos<line.size();){
      size_t output_pos = pos;

      dict.match(line, pos, &output_str, &output_pos);
      if(output_str==NULL){
        nolink_part.push_back(line[pos]);
        pos+=1;
      } else {
        if(nolink_part.size()){
          std::wcout<<nolink_part<<std::endl;
          nolink_part.clear();
        }
        std::wcout<<line.substr(pos, output_pos-pos)<<'\t'<<*output_str<<std::endl;
        pos = output_pos;
      }
    }
    if(nolink_part.size()){
      std::wcout<<nolink_part<<std::endl;
      nolink_part.clear();
    }
    std::wcout<<std::endl;
  }
}

void handleHitMode(InversedDict& dict){
  std::wstring line;
  while(true){
    std::getline(std::wcin, line);
    if(!line.size()){
      std::cerr<<"null string received, exiting."<<std::endl;
      break;
    }

    std::wstring* output_str;
    std::wstring nolink_part;

    for(size_t pos=0;pos<line.size();pos++){
      size_t output_pos = pos;

      dict.match(line, pos, &output_str, &output_pos);
      if(output_str!=NULL){
        std::wcout<<line.substr(pos, output_pos-pos)<<'\t'<<*output_str<<std::endl;
      }
    }
    std::wcout<<std::endl;
  }
}
int main(int argc, char** argv){
  InversedDict dict;

  std::wstring line;
  while(true){
    std::getline(std::wcin, line);
    if(!line.size()){
      std::cerr<<"all key-value pairs are read."<<std::endl;
      break;
    }

    size_t pos = line.find(L'\t');
    if(pos == std::wstring::npos){
      std::cerr<<"No tab char found in input"<<std::endl;
      return -1;
    }

    std::wstring
      key(line, 0, pos),
      value(line, pos+1);

    dict.set(key, value);
  }

  if(argc == 1){
    handleContinuousMode(dict);
  }else if(argc == 2 && strcmp(argv[1], "-hit")==0){
    handleHitMode(dict);
  }else{
    std::cerr<<"-hit: hit mode, will print every tokens in dictionary"<<std::endl;
    std::cerr<<"or will run in normal mode, input will be split into tokens"<<std::endl;
    return 1;
  }

  std::cerr<<"really exiting..."<<std::endl;

  return 0;
}
