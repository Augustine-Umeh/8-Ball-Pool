#include "phylib.h"

// int main(int argc, char const *argv[])
// {
//     printf("Working");
//     return 0;
// }

phylib_object *phylib_new_still_ball(unsigned char number, phylib_coord *pos)
{
    // Allocating memory
    phylib_object *new_object = (phylib_object *)malloc(sizeof(phylib_object));
    if (new_object == NULL)
    {
        return NULL; // If malloc fails return NULL
    }
    new_object->type = PHYLIB_STILL_BALL;
    new_object->obj.still_ball.number = number;
    new_object->obj.still_ball.pos = *pos;

    return new_object;
}

phylib_object *phylib_new_rolling_ball(unsigned char number,
                                       phylib_coord *pos,
                                       phylib_coord *vel,
                                       phylib_coord *acc)
{
    phylib_object *new_object = (phylib_object *)malloc(sizeof(phylib_object));
    if (new_object == NULL)
    {
        return NULL; // If malloc fails return NULL
    }

    new_object->type = PHYLIB_ROLLING_BALL;
    new_object->obj.rolling_ball.number = number;
    new_object->obj.rolling_ball.pos = *pos;
    new_object->obj.rolling_ball.vel = *vel;
    new_object->obj.rolling_ball.acc = *acc;

    return new_object;
}

phylib_object *phylib_new_hole(phylib_coord *pos)
{
    phylib_object *new_object = (phylib_object *)malloc(sizeof(phylib_object));
    if (new_object == NULL)
    {
        return NULL; // Memory allocation failed
    }

    new_object->type = PHYLIB_HOLE;
    new_object->obj.hole.pos = *pos;

    return new_object;
}

phylib_object *phylib_new_hcushion(double y)
{
    phylib_object *new_object = (phylib_object *)malloc(sizeof(phylib_object));
    if (new_object == NULL)
    {
        return NULL; // Memory allocation failed
    }

    new_object->type = PHYLIB_HCUSHION;
    new_object->obj.hcushion.y = y;

    return new_object;
}

phylib_object *phylib_new_vcushion(double x)
{
    phylib_object *new_object = (phylib_object *)malloc(sizeof(phylib_object));
    if (new_object == NULL)
    {
        return NULL; // Memory allocation failed
    }

    new_object->type = PHYLIB_VCUSHION;
    new_object->obj.vcushion.x = x;

    return new_object;
}

phylib_table *phylib_new_table(void)
{
    phylib_table *new_table = (phylib_table *)malloc(sizeof(phylib_table));
    if (new_table == NULL)
    {
        return NULL; // Memory allocation failed
    }

    new_table->time = 0.0;

    // Allocate and initialize objects for the table
    new_table->object[0] = phylib_new_hcushion(0.0);
    new_table->object[1] = phylib_new_hcushion(PHYLIB_TABLE_LENGTH);
    new_table->object[2] = phylib_new_vcushion(0.0);
    new_table->object[3] = phylib_new_vcushion(PHYLIB_TABLE_WIDTH);

    // Create holes
    new_table->object[4] = phylib_new_hole(&(phylib_coord){0.0, 0.0});
    new_table->object[5] = phylib_new_hole(&(phylib_coord){0.0, PHYLIB_TABLE_WIDTH});
    new_table->object[6] = phylib_new_hole(&(phylib_coord){0.0, PHYLIB_TABLE_LENGTH});
    new_table->object[7] = phylib_new_hole(&(phylib_coord){PHYLIB_TABLE_WIDTH, 0.0});
    new_table->object[8] = phylib_new_hole(&(phylib_coord){PHYLIB_TABLE_WIDTH, PHYLIB_TABLE_LENGTH / 2.0});
    new_table->object[9] = phylib_new_hole(&(phylib_coord){PHYLIB_TABLE_WIDTH, PHYLIB_TABLE_LENGTH});

    for (int i = 10; i < PHYLIB_MAX_OBJECTS; ++i)
    {
        new_table->object[i] = NULL; // Initialize remaining pointers to NULL
    }

    return new_table;
}

// Part 2 functions

void phylib_copy_object(phylib_object **dest, phylib_object **src)
{
    if (src == NULL || *src == NULL)
    {
        *dest = NULL; // If src is NULL or points to NULL, set dest to NULL
    }
    else
    {
        // Allocate memory for new object
        *dest = (phylib_object *)malloc(sizeof(phylib_object));

        if (*dest != NULL) // Allocation error
        {
            memcpy(*dest, *src, sizeof(phylib_object)); // Copying object from source to destination
        }
        else
        {
            *dest = NULL;
        }
    }
}

phylib_table *phylib_copy_table(phylib_table *table)
{
    if (table == NULL)
    {
        return NULL; // If table is NULL, return NULL
    }

    // Allocate memory for new table
    phylib_table *new_table = (phylib_table *)malloc(sizeof(phylib_table));

    if (new_table != NULL) // If not Allocation error
    {
        // Copying table
        memcpy(new_table, table, sizeof(phylib_table));
    }

    // Copy the objects array
    for (int i = 0; i < PHYLIB_MAX_OBJECTS; ++i)
    {
        if (table->object[i] != NULL)
        {
            // Allocate memory for the new object
            phylib_object *new_object = (phylib_object *)malloc(sizeof(phylib_object));

            if (new_object != NULL)
            {
                // Copy the object content
                memcpy(new_object, table->object[i], sizeof(phylib_object));
                new_table->object[i] = new_object;
            }
        }
    }

    return new_table;
}

void phylib_add_object(phylib_table *table, phylib_object *object)
{
    if (table == NULL || object == NULL)
    {
        return; // If table or object is null, exit
    }

    // Iterate over the object array in the table to find a NULL pointer
    for (int i = 0; i < PHYLIB_MAX_OBJECTS; ++i)
    {
        if (table->object[i] == NULL)
        {
            // Found a NULL pointer, assign it to the address of the object
            table->object[i] = object;
            return;
        }
    }

    // If no NULL pointers were found, do nothing
}

void phylib_free_table(phylib_table *table)
{

    if (table == NULL)
    {
        return;
    }

    // Iterate through the objects in the table
    for (int i = 0; i < PHYLIB_MAX_OBJECTS; i++)
    {
        if (table->object[i] != NULL)
        {
            free(table->object[i]);
            table->object[i] = NULL;
        }
    }

    free(table);
}

phylib_coord phylib_sub(phylib_coord c1, phylib_coord c2)
{
    phylib_coord result;

    // Subtracting coords
    result.x = c1.x - c2.x;
    result.y = c1.y - c2.y;

    return result;
}

double phylib_length(phylib_coord c)
{
    double length = sqrt((c.x * c.x) + (c.y * c.y));

    return length;
}

double phylib_dot_product(phylib_coord a, phylib_coord b)
{
    double product = (a.x * b.x) + (a.y * b.y);

    return product;
}

// Calculate distance between two coordinates
double coord_distance(phylib_coord c1, phylib_coord c2)
{
    return sqrt(((c1.x - c2.x) * (c1.x - c2.x)) + ((c1.y - c2.y) * (c1.y - c2.y)));
}

// Calculate distance between two objects
double phylib_distance(phylib_object *obj1, phylib_object *obj2)
{
    if (obj1 == NULL || obj2 == NULL)
    {
        return -1.0; // Invalid input objects
    }

    if (obj1->type != PHYLIB_ROLLING_BALL)
    {
        return -1.0; // obj1 must be a PHYLIB_ROLLING_BALL
    }

    phylib_coord center_obj1 = obj1->obj.rolling_ball.pos;

    switch (obj2->type)
    {
    case PHYLIB_ROLLING_BALL:
    case PHYLIB_STILL_BALL: // Ball and Ball minus both radius'
        return coord_distance(center_obj1, obj2->obj.still_ball.pos) - PHYLIB_BALL_DIAMETER;

    case PHYLIB_HOLE: // Ball and hole minus hole radius
        return coord_distance(center_obj1, obj2->obj.hole.pos) - PHYLIB_HOLE_RADIUS;

    case PHYLIB_HCUSHION: // Ball and h-cushion minus ball radius
        return fabs(center_obj1.y - obj2->obj.hcushion.y) - PHYLIB_BALL_RADIUS;

    case PHYLIB_VCUSHION: // Ball and v-cushion minus ball radius
        return fabs(center_obj1.x - obj2->obj.vcushion.x) - PHYLIB_BALL_RADIUS;
        // -4 - 1350 = 1354 - 28.5 = 
    default: // Invalid obj2 type
        return -1.0;
    }
}

// Part 3
void phylib_roll(phylib_object *new, phylib_object *old, double time)
{
    if (new == NULL || old == NULL)
    {
        return; // if objs null, exit
    }

    if (new->type != PHYLIB_ROLLING_BALL || old->type != PHYLIB_ROLLING_BALL)
    {
        return; // If either one is not rolling, exit
    }

    // Calculating new position
    new->obj.rolling_ball.pos.x = (old->obj.rolling_ball.pos.x) +
                                  (old->obj.rolling_ball.vel.x * time) +
                                  (0.5 * old->obj.rolling_ball.acc.x * (time * time));

    new->obj.rolling_ball.pos.y = (old->obj.rolling_ball.pos.y) +
                                  (old->obj.rolling_ball.vel.y * time) +
                                  (0.5 * old->obj.rolling_ball.acc.y * (time * time));

    // Calculating new velocity
    new->obj.rolling_ball.vel.x = old->obj.rolling_ball.vel.x + (old->obj.rolling_ball.acc.x * time);
    new->obj.rolling_ball.vel.y = old->obj.rolling_ball.vel.y + (old->obj.rolling_ball.acc.y * time);

    // Checking for sign changes
    if ((old->obj.rolling_ball.vel.x * new->obj.rolling_ball.vel.x) < 0.0)
    {
        new->obj.rolling_ball.vel.x = 0.0;
        new->obj.rolling_ball.acc.x = 0.0;
    }

    if ((old->obj.rolling_ball.vel.y * new->obj.rolling_ball.vel.y) < 0.0)
    {
        new->obj.rolling_ball.vel.y = 0.0;
        new->obj.rolling_ball.acc.y = 0.0;
    }
}

unsigned char phylib_stopped(phylib_object *object)
{
    if (object == NULL || object->type != PHYLIB_ROLLING_BALL)
    {
        return 0; // if object is NULL or not a rolling ball, return 0
    }

    // Calculating speed of rolling ball (length of velocity)
    double speed = sqrt(object->obj.rolling_ball.vel.x * object->obj.rolling_ball.vel.x +
                        object->obj.rolling_ball.vel.y * object->obj.rolling_ball.vel.y);

    if (speed < PHYLIB_VEL_EPSILON)
    {
        // Convert ROLLING_BALL to STILL_BALL
        object->type = PHYLIB_STILL_BALL;
        return 1; // Return 1 if ball was converted
    }

    return 0; // Return 0 if the ball has not stopped
}

void phylib_bounce(phylib_object **a, phylib_object **b)
{
    if (a == NULL || b == NULL || *a == NULL || *b == NULL)
    {
        return;
    }

    phylib_object *objA = *a;
    phylib_object *objB = *b;

    if (objA->type != PHYLIB_ROLLING_BALL)
    {
        return; // a is not ROLLING_BALL, do nothing
    }

    switch (objB->type)
    {
    case PHYLIB_HCUSHION: // Case 1
        objA->obj.rolling_ball.vel.y = -objA->obj.rolling_ball.vel.y;
        objA->obj.rolling_ball.acc.y = -objA->obj.rolling_ball.acc.y;
        break;

    case PHYLIB_VCUSHION: // Case 2
        objA->obj.rolling_ball.vel.x = -objA->obj.rolling_ball.vel.x;
        objA->obj.rolling_ball.acc.x = -objA->obj.rolling_ball.acc.x;
        break;

    case PHYLIB_HOLE: // Case 3
        // Free memory of a and set it to NULL
        free(*a);
        *a = NULL;
        break;

    case PHYLIB_STILL_BALL: // Case 4
        // Upgrade the type and proceed to next case
        objB->type = PHYLIB_ROLLING_BALL;
        objB->obj.rolling_ball.vel.x = 0.0;
        objB->obj.rolling_ball.vel.y = 0.0;
        objB->obj.rolling_ball.acc.x = 0.0;
        objB->obj.rolling_ball.acc.y = 0.0;

    case PHYLIB_ROLLING_BALL: // Case 5
    {
        // Compute position of A with respect to B, r_ab
        phylib_coord r_ab = phylib_sub(objA->obj.rolling_ball.pos, objB->obj.rolling_ball.pos);

        // Compute relative velocity of A with respect to B, v_rel
        phylib_coord v_rel = phylib_sub(objA->obj.rolling_ball.vel, objB->obj.rolling_ball.vel);

        // Compute the normal vector, n
        phylib_coord n = {r_ab.x / phylib_length(r_ab), r_ab.y / phylib_length(r_ab)};

        // Calculate the dot product of v_rel with respect to n, v_rel_n
        double v_rel_n = phylib_dot_product(v_rel, n);

        // Update velocities of a and b
        objA->obj.rolling_ball.vel.x -= v_rel_n * n.x;
        objA->obj.rolling_ball.vel.y -= v_rel_n * n.y;

        objB->obj.rolling_ball.vel.x += v_rel_n * n.x;
        objB->obj.rolling_ball.vel.y += v_rel_n * n.y;

        // Compute speeds of a and b
        double speedA = phylib_length(objA->obj.rolling_ball.vel);
        double speedB = phylib_length(objB->obj.rolling_ball.vel);

        // Check if the speeds are greater than PHYLIB_VEL_EPSILON
        if (speedA > PHYLIB_VEL_EPSILON)
        {
            // Set acceleration to the negative velocity divided by the speed, multiplied by PHYLIB_DRAG
            objA->obj.rolling_ball.acc.x = (-objA->obj.rolling_ball.vel.x / speedA) * PHYLIB_DRAG;
            objA->obj.rolling_ball.acc.y = (-objA->obj.rolling_ball.vel.y / speedA) * PHYLIB_DRAG;
        }

        if (speedB > PHYLIB_VEL_EPSILON)
        {
            objB->obj.rolling_ball.acc.x = (-objB->obj.rolling_ball.vel.x / speedB) * PHYLIB_DRAG;
            objB->obj.rolling_ball.acc.y = (-objB->obj.rolling_ball.vel.y / speedB) * PHYLIB_DRAG;
        }
        break;
    }

    default:
        return;
    }
}

unsigned char phylib_rolling(phylib_table *t)
{
    if (t == NULL)
    {
        return 0; // if table is NULL, return 0
    }

    unsigned char rollingCount = 0;

    // Counting rolling balls
    for (int i = 0; i < PHYLIB_MAX_OBJECTS; ++i)
    {
        if (t->object[i] != NULL && t->object[i]->type == PHYLIB_ROLLING_BALL)
        {
            rollingCount++;
        }
    }

    return rollingCount;
}

phylib_table *phylib_segment(phylib_table *table)
{
    double time_passed = PHYLIB_SIM_RATE;

    if (table == NULL)
    {
        return NULL;
    }

    if (phylib_rolling(table) == 0)
    {
        return NULL;
    }

    // Copying Table
    phylib_table *copyTable = phylib_copy_table(table);

    if (copyTable == NULL)
    {
        return NULL;
    }

    while (time_passed <= PHYLIB_MAX_TIME)
    {
        // Loop Throguh and roll all rolling balls
        for (int i = 0; i < PHYLIB_MAX_OBJECTS; i++)
        {
            if (copyTable->object[i] != NULL && copyTable->object[i]->type == PHYLIB_ROLLING_BALL)
            {
                // Calling Roll on every rolling ball
                phylib_roll(copyTable->object[i], table->object[i], time_passed);
            }
        }

        //  Loop again and check if stopped or collision
        for (int i = 0; i < PHYLIB_MAX_OBJECTS; i++)
        {
            if (copyTable->object[i] != NULL && copyTable->object[i]->type == PHYLIB_ROLLING_BALL)
            {

                // Check if the ROLLING_BALL stopped
                if (phylib_stopped(copyTable->object[i]) == 1)
                {
                    copyTable->time += time_passed;
                    return copyTable;
                }

                // Check for phylib_distance less than 0.0
                for (int j = 0; j < PHYLIB_MAX_OBJECTS; ++j)
                {
                    if (i != j && copyTable->object[j] != NULL)
                    {
                        double distance = phylib_distance(copyTable->object[i], copyTable->object[j]);
                        if (distance < 0.0)
                        {
                            copyTable->time += time_passed;
                            phylib_bounce(&copyTable->object[i], &copyTable->object[j]);
                            return copyTable;
                        }
                    }
                }
            }
        }

        time_passed += PHYLIB_SIM_RATE;
    }

    return copyTable;
}

char *phylib_object_string(phylib_object *object)
{
    static char string[80];
    if (object == NULL)
    {
        snprintf(string, 80, "NULL;");
        return string;
    }
    switch (object->type)
    {
    case PHYLIB_STILL_BALL:
        snprintf(string, 80,
                 "STILL_BALL (%d,%6.1lf,%6.1lf)",
                 object->obj.still_ball.number,
                 object->obj.still_ball.pos.x,
                 object->obj.still_ball.pos.y);
        break;
    case PHYLIB_ROLLING_BALL:
        snprintf(string, 80,
                 "ROLLING_BALL (%d,%6.1lf,%6.1lf,%6.1lf,%6.1lf,%6.1lf,%6.1lf)",
                 object->obj.rolling_ball.number,
                 object->obj.rolling_ball.pos.x,
                 object->obj.rolling_ball.pos.y,
                 object->obj.rolling_ball.vel.x,
                 object->obj.rolling_ball.vel.y,
                 object->obj.rolling_ball.acc.x,
                 object->obj.rolling_ball.acc.y);
        break;
    case PHYLIB_HOLE:
        snprintf(string, 80,
                 "HOLE (%6.1lf,%6.1lf)",
                 object->obj.hole.pos.x,
                 object->obj.hole.pos.y);
        break;
    case PHYLIB_HCUSHION:
        snprintf(string, 80,
                 "HCUSHION (%6.1lf)",
                 object->obj.hcushion.y);
        break;
    case PHYLIB_VCUSHION:
        snprintf(string, 80,
                 "VCUSHION (%6.1lf)",
                 object->obj.vcushion.x);
        break;
    }
    return string;
}
