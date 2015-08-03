#include <iostream>
#include <vector>
#include <cstdlib>
#include <utility>
#include <map>
#include <stack>
#include <cmath>
#include <sstream>
#include <algorithm>

class TreeNodeStorage{
public:
  int id;
  std::vector<int> inlinks;
  std::vector<int> outlinks;
  std::vector<float> values;
  int visited;
};

template<typename T>
std::vector<T> readFromString(const std::string& str){
  std::vector<T> result;
  std::stringstream stream(str);

  while(true){
    T v;
    stream >> v;
    if(!stream.fail())
      result.push_back(v);
    else
      break;
  }

  return result;
}
void inLinkToTree(std::map<int, TreeNodeStorage>& storage, std::vector<int>& roots, size_t& ndim){
  std::vector<int> noinlinks;
  // build all nodes
  for(auto i=storage.begin();i!=storage.end();++i){
    TreeNodeStorage& node = i->second;
    for(size_t j=0;j<node.inlinks.size();++j){
      int inlinkId = node.inlinks[j];
      storage[inlinkId].outlinks.push_back(i->first);
    }

    if(node.inlinks.size()==0){
      noinlinks.push_back(i->first);
    }
  }

  std::cerr<<"Please enter initial vectors in form: "<<
    "nodeId value0 value1 ..."<<std::endl<<
    "end them using a blank line (CR)"<<std::endl;

  ndim = 0;
  while(true){
    std::string tmp;
    std::getline(std::cin, tmp);
    if(tmp.size()==0)
      break;

    int id = std::atoi(tmp.c_str());
    TreeNodeStorage& node=storage[id];
    size_t space = tmp.find(' ');

    std::string values;
    values.assign(tmp, space+1);

    std::vector<float> valuesf = readFromString<float>(values);
    ndim = std::max(ndim, valuesf.size());

    node.values.swap(valuesf);

    roots.push_back(id);

    auto it = std::find(noinlinks.begin(), noinlinks.end(), id);
    if(it!=noinlinks.end()){
      noinlinks.erase(it);
    }
  }

  for(size_t i=0;i<noinlinks.size();++i){
    std::cerr<<"No initial values for root node "
             <<noinlinks[i]<<std::endl;
  }

  for(auto i=storage.begin();i!=storage.end();++i){
    TreeNodeStorage& node=i->second;
    if(node.values.size()==0){
      node.values.assign(ndim, 0.0f);
    }
  }
}

void iterate(std::map<int, TreeNodeStorage>& storage, std::vector<int>& roots, size_t& ndim){
  float accumulate;

  for(auto i=storage.begin();i!=storage.end();++i){
    i->second.visited = -1;
  }

  int iter = 0;
  std::stack<int> tovisit;
  float* values = new float[ndim];

  while(true){
    accumulate = 0.0f;
    iter += 1;

    for(size_t i=0;i<roots.size();++i){
      std::vector<int>& outlinks = storage[roots[i]].outlinks;
      storage[roots[i]].visited = iter;
      for(size_t j=0;j<outlinks.size();++j)
        tovisit.push(outlinks[j]);
    }

    while(!tovisit.empty()){
      int id = tovisit.top();
      TreeNodeStorage& node = storage[id];
      tovisit.pop();

      if(node.visited == iter)
        continue;

      node.visited = iter;

      for(size_t i=0;i<node.outlinks.size();++i)
        tovisit.push(node.outlinks[i]);

      for(size_t i=0;i<ndim;++i) values[i] = 0.0f;

      for(size_t i=0;i<node.inlinks.size();++i){
        TreeNodeStorage& inlink = storage[node.inlinks[i]];
        for(size_t j=0;j<ndim;++j)
          values[j] += inlink.values[j];
      }

      float norm = 0.0f;
      for(size_t i=0;i<ndim;++i){
        norm += values[i]*values[i];
      }
      norm = std::sqrt(norm);

      if(norm<0.0000001)
        continue;

      for(size_t i=0;i<ndim;++i){
        float v = values[i] / norm;
        accumulate += std::abs(v - node.values[i]);
        node.values[i] = v;
      }
    }

    std::cerr<<"Iter "<<iter<<", accumulate "<<accumulate<<std::endl;
    if(accumulate<0.0001)
      break;
  }

  delete[] values;
}
std::map<int, TreeNodeStorage> readInLink(){
  std::cerr<<"Distribute a quasi-tree in a N-dimensional space"
           <<std::endl;
  std::cerr<<"Please enter nodes now, "
    "end them using a blank line (CR)"
           <<std::endl;

  std::map<int, TreeNodeStorage> tree_inlink;

  while(true){
    std::string tmp;
    std::getline(std::cin, tmp);
    if(!tmp.size())
      break;

    TreeNodeStorage storage;
    int id = atoi(tmp.c_str());
    storage.id = id;
    tree_inlink[id] = storage;
  }

  std::cerr<<"Please enter node links in form: "
    "treeId inlinkId, end them "
    "using a blank line (CR)."<<std::endl;

  while(true){
    std::string tmp;
    std::getline(std::cin, tmp);
    if(!tmp.size())
      break;

    size_t space = tmp.find(' ');
    if (space==std::string::npos)
      break;

    int treeId = atoi(tmp.c_str()),
      inlinkId = atoi(tmp.c_str() + space + 1);

    tree_inlink[treeId].inlinks.push_back(inlinkId);
  }

  return tree_inlink;
}


int main(int, char**){
  std::map<int, TreeNodeStorage> tree = readInLink();
  std::vector<int> roots;
  size_t ndim;

  inLinkToTree(tree, roots, ndim);

  std::cout<<"roots: ";
  for(size_t i=0;i<roots.size();++i)
    std::cout<<roots[i]<<' ';
  std::cout<<std::endl;

  iterate(tree, roots, ndim);

  for(auto i=tree.begin();i!=tree.end();++i){
    std::cout<<i->first<<' ';
    for(size_t j=0;j<i->second.values.size();++j)
      std::cout<<i->second.values[j]<<' ';
    std::cout<<std::endl;
  }
  return 0;
}
