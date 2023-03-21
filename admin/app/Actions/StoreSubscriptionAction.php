<?php
namespace App\Actions;

use App\Models\Subscription;


class  StoreSubscriptionAction
{

    public function execute($data){

        return Subscription::create($data);

    }
}

