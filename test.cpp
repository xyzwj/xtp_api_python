/*g++ test.cpp -lboost_system -lboost_thread -lboost_filesystem -lpthread -o test */
#include <boost/thread/thread.hpp>
#include <iostream>
using namespace boost;

void test()
{
    std::cout<<"hello world!"<<std::endl;
}
int main(int argc, char const *argv[]) {
    boost::thread  t1(&test);
    t1.join();
    return 0;
}
