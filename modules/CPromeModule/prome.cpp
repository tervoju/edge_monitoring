#include <prometheus/counter.h>
#include <prometheus/exposer.h>
#include <prometheus/registry.h>

#include <array>
#include <chrono>
#include <cstdlib>
#include <memory>
#include <string>
#include <pthread.h>

void* prome(void *arg)
{

    // detach the current thread
    // from the calling thread
    pthread_detach(pthread_self());
    // create an http server running on port 8080
    auto exposer = Exposer{"127.0.0.1:8080"};

    // create a metrics registry with component=main labels applied to all its
    // metrics
    auto registry = std::make_shared<Registry>();

    // add a new counter family to the registry (families combine values with the
    // same name, but distinct label dimenstions)
    auto &counter_family = BuildCounter()
                               .Name("time_running_seconds")
                               .Help("How many seconds is this server running?")
                               .Labels({{"label", "value"}})
                               .Register(*registry);

    // add a counter to the metric family
    auto &second_counter = counter_family.Add(
        {{"another_label", "value"}, {"yet_another_label", "value"}});

    // ask the exposer to scrape the registry on incoming scrapes
    exposer.RegisterCollectable(registry);

    for (;;)
    {
        std::this_thread::sleep_for(std::chrono::seconds(1));
        // increment the counter by one (second)
        second_counter.Increment();
    }
    // exit the current thread
    pthread_exit(NULL);
    return 0;
}